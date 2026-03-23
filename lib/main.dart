import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'screens/dashboard_screen.dart';
import 'screens/kasir_screen.dart';
import 'screens/inventaris_screen.dart';
import 'models/transaction_model.dart';

void main() {
  runApp(const DesktopKasirApp());
}

class DesktopKasirApp extends StatelessWidget {
  const DesktopKasirApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Sistem Kasir Toko Papa',
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(elevation: 4, centerTitle: false),
      ),
      home: const MainDashboard(),
    );
  }
}

class MainDashboard extends StatefulWidget {
  const MainDashboard({super.key});

  @override
  State<MainDashboard> createState() => _MainDashboardState();
}

class _MainDashboardState extends State<MainDashboard> {
  final String apiUrl = 'http://localhost:8000/api';

  // ==== STATE VARIABLES ====
  int halamanAktif = 0; // 0 = Kasir, 1 = Dashboard, 2 = Inventaris
  List<dynamic> daftarBarang = [];
  List<dynamic> keranjang = [];
  int totalBayar = 0;
  List<dynamic> daftarLaporan = [];
  List<Transaction> transactions = [];
  bool isLoading = false;
  int omzetHariIni = 0;
  List<dynamic> topProduk = [];
  String? lastError;
  int retryCount = 0;
  final int maxRetries = 3;
  final Duration requestTimeout = const Duration(seconds: 15);
  String searchQuery = "";
  List<dynamic> daftarBarangFiltered = [];
  double discountPercent = 0.0;
  int discountAmount = 0;
  String promoCode = "";

  // Controllers
  late TextEditingController scanCtrl;

  @override
  void initState() {
    super.initState();
    scanCtrl = TextEditingController();
    _initializeApp();
  }

  @override
  void dispose() {
    scanCtrl.dispose();
    super.dispose();
  }

  // ==== VALIDATION HELPERS ====
  String _validateProductInput(
    String nama,
    String kategori,
    String harga,
    String stok,
  ) {
    if (nama.trim().isEmpty) return "Nama barang tidak boleh kosong";
    if (kategori.trim().isEmpty) return "Kategori tidak boleh kosong";
    if (harga.trim().isEmpty) return "Harga tidak boleh kosong";
    if (stok.trim().isEmpty) return "Stok tidak boleh kosong";

    int? hrg = int.tryParse(harga.trim());
    if (hrg == null || hrg <= 0) return "Harga harus angka positif";

    int? stk = int.tryParse(stok.trim());
    if (stk == null || stk < 0) return "Stok harus angka non-negatif";

    if (nama.length > 100)
      return "Nama barang terlalu panjang (max 100 karakter)";
    return "";
  }

  String _getFriendlyErrorMsg(dynamic error) {
    if (error is TimeoutException) {
      return "Koneksi timeout - periksa internet Anda";
    } else if (error is FormatException) {
      return "Format data tidak valid";
    } else if (error.toString().contains("Connection refused")) {
      return "Tidak bisa terhubung ke server - pastikan backend running";
    } else if (error.toString().contains("SocketException")) {
      return "Error jaringan - periksa koneksi internet";
    }
    return error.toString();
  }

  Future<void> _initializeApp() async {
    await refreshData();
    await ambilStats();
  }

  // ==== API FUNCTIONS ====

  Future<void> refreshData({int attempt = 0}) async {
    setState(() => isLoading = true);
    try {
      final res = await http
          .get(Uri.parse('$apiUrl/cek-barang'))
          .timeout(
            requestTimeout,
            onTimeout: () => throw TimeoutException('Request timeout'),
          );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          daftarBarang = (data is List ? data : [data]);
          daftarBarangFiltered = daftarBarang; // Sync filtered list
          lastError = null;
          retryCount = 0;
        });
      } else if (res.statusCode == 500 && attempt < maxRetries) {
        await Future.delayed(const Duration(seconds: 2));
        return refreshData(attempt: attempt + 1);
      } else {
        setState(() => lastError = 'Server Error: ${res.statusCode}');
        _showNotification(
          'Gagal memuat data barang (${res.statusCode})',
          Colors.red,
        );
      }
    } on TimeoutException {
      if (attempt < maxRetries) {
        print('Timeout, retry attempt $attempt');
        await Future.delayed(const Duration(seconds: 1));
        return refreshData(attempt: attempt + 1);
      } else {
        setState(() => lastError = 'Koneksi timeout, periksa internet Anda');
        _showNotification(
          'Koneksi timeout. Periksa internet Anda.',
          Colors.red,
        );
      }
    } catch (e) {
      print("Error Refresh: $e");
      setState(() => lastError = e.toString());
      _showNotification('Error: ${_getFriendlyErrorMsg(e)}', Colors.red);
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> ambilStats() async {
    try {
      final res = await http
          .get(Uri.parse('$apiUrl/dashboard-stats'))
          .timeout(
            requestTimeout,
            onTimeout: () => throw TimeoutException('Request timeout'),
          );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          omzetHariIni = data['omzet'] ?? 0;
          topProduk = data['top_produk'] ?? [];
        });
      }
    } catch (e) {
      print("Error Ambil Stats: $e");
    }
  }

  Future<void> prosesRestok(int id, int jumlah) async {
    try {
      final response = await http
          .post(
            Uri.parse('$apiUrl/restok'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'id': id, 'jumlah': jumlah}),
          )
          .timeout(
            requestTimeout,
            onTimeout: () => throw TimeoutException('Request timeout'),
          );

      if (response.statusCode == 200) {
        _showNotification('✓ Stok berhasil diperbarui!', Colors.green);
        await refreshData();
      } else {
        _showNotification(
          'Gagal update stok (${response.statusCode})',
          Colors.red,
        );
      }
    } on TimeoutException {
      _showNotification('Timeout saat update stok', Colors.red);
    } catch (e) {
      print("Error Restok: $e");
      _showNotification('Error: ${_getFriendlyErrorMsg(e)}', Colors.red);
    }
  }

  Future<void> simpanBarangBaru(
    String nama,
    String kategori,
    String harga,
    String stok,
  ) async {
    // === INPUT VALIDATION ===
    String validasi = _validateProductInput(nama, kategori, harga, stok);
    if (validasi.isNotEmpty) {
      _showNotification(validasi, Colors.orange);
      return;
    }

    try {
      final res = await http
          .post(
            Uri.parse('$apiUrl/tambah-barang'),
            body: {
              'nama': nama.trim(),
              'kategori': kategori.trim(),
              'harga': harga.trim(),
              'stok': stok.trim(),
            },
          )
          .timeout(
            requestTimeout,
            onTimeout: () => throw TimeoutException('Request timeout'),
          );

      if (res.statusCode == 200) {
        _showNotification('✓ Barang berhasil ditambahkan!', Colors.green);
        await refreshData();
        if (mounted) Navigator.pop(context);
      } else {
        _showNotification(
          'Gagal menambahkan barang (${res.statusCode})',
          Colors.red,
        );
      }
    } on TimeoutException {
      _showNotification('Koneksi timeout. Periksa internet Anda.', Colors.red);
    } catch (e) {
      print("Gagal Simpan: $e");
      _showNotification('Error: ${_getFriendlyErrorMsg(e)}', Colors.red);
    }
  }

  Future<void> prosesCheckout() async {
    if (keranjang.isEmpty) {
      _showNotification("Keranjang kosong!", Colors.orange);
      return;
    }

    if (totalBayar <= 0) {
      _showNotification("Total pembayaran tidak valid!", Colors.orange);
      return;
    }

    setState(() => isLoading = true);

    try {
      List dataKeranjang = keranjang
          .map((item) => {'id': item['id'], 'qty': item['qty']})
          .toList();

      final res = await http
          .post(
            Uri.parse('$apiUrl/checkout'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'items': dataKeranjang}),
          )
          .timeout(
            requestTimeout,
            onTimeout: () => throw TimeoutException('Checkout timeout'),
          );

      if (res.statusCode == 200) {
        // Save transaction to local history with discount info
        int subtotal = keranjang.fold(
          0,
          (sum, k) => sum + (_parseHarga(k['harga']) * (k['qty'] as int)),
        );

        // Convert keranjang items to proper transaction items format
        List<Map<String, dynamic>> transactionItems = keranjang.map((item) {
          int itemHarga = _parseHarga(item['harga']);
          return {
            'id': item['id'] ?? 0,
            'nama': item['nama'] ?? 'Unknown Product',
            'harga': itemHarga,
            'qty': item['qty'] ?? 1,
          };
        }).toList();

        Transaction newTransaction = Transaction(
          id: transactions.length + 1,
          transactionId: 'TRX-${DateTime.now().millisecondsSinceEpoch}',
          items: transactionItems,
          subtotal: subtotal,
          discount: discountAmount,
          discountPercent: discountPercent,
          discountCode: promoCode,
          finalTotal: totalBayar,
          dateTime: DateTime.now(),
          paymentStatus: 'success',
        );

        setState(() {
          transactions.insert(0, newTransaction);
        });

        _showNotification(
          "✓ Transaksi Berhasil! (${newTransaction.transactionId})",
          Colors.green,
        );
        _kosongkanKeranjang();
        await refreshData();
        await ambilStats();
      } else {
        _showNotification("Gagal di server: ${res.statusCode}", Colors.red);
      }
    } on TimeoutException {
      _showNotification(
        'Checkout timeout. Periksa koneksi internet.',
        Colors.red,
      );
    } catch (e) {
      print("Error Checkout: $e");
      _showNotification("Error: ${_getFriendlyErrorMsg(e)}", Colors.red);
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> ambilLaporan() async {
    try {
      final res = await http
          .get(Uri.parse('$apiUrl/laporan'))
          .timeout(
            requestTimeout,
            onTimeout: () => throw TimeoutException('Request timeout'),
          );
      if (res.statusCode == 200) {
        setState(() {
          daftarLaporan = jsonDecode(res.body);
        });
      }
    } on TimeoutException {
      _showNotification('Timeout memuat riwayat', Colors.red);
    } catch (e) {
      print("Error Ambil Laporan: $e");
      _showNotification('Error: ${_getFriendlyErrorMsg(e)}', Colors.red);
    }
  }

  // ==== UI/CART FUNCTIONS ====

  int _parseHarga(dynamic harga) {
    try {
      if (harga == null) return 0;
      String hrg = harga.toString().trim();
      if (hrg.isEmpty) return 0;
      // Handle decimal numbers
      if (hrg.contains('.')) {
        return int.parse(hrg.split('.')[0]);
      }
      // Handle currency format (e.g., "25000.50")
      return int.parse(hrg.replaceAll(RegExp(r'[^0-9]'), ''));
    } catch (e) {
      print('Error parsing harga: $harga, error: $e');
      return 0;
    }
  }

  void _tambahKeKeranjang(Map<dynamic, dynamic> item) {
    setState(() {
      int indexKetemu = keranjang.indexWhere((k) => k['id'] == item['id']);
      if (indexKetemu != -1) {
        keranjang[indexKetemu]['qty'] += 1;
      } else {
        keranjang.add({
          'id': item['id'],
          'nama': item['nama_barang'],
          'harga': _parseHarga(item['harga']),
          'qty': 1,
        });
      }
      _hitungTotal();
    });
  }

  void _updateKeranjangQty(int index, int newQty) {
    setState(() {
      if (newQty <= 0) {
        keranjang.removeAt(index);
      } else {
        keranjang[index]['qty'] = newQty;
      }
      _hitungTotal();
    });
  }

  void _cariProduk(String query) {
    setState(() {
      searchQuery = query.toLowerCase();
      if (searchQuery.isEmpty) {
        daftarBarangFiltered = daftarBarang;
      } else {
        daftarBarangFiltered = daftarBarang
            .where(
              (item) =>
                  (item['nama_barang'] ?? '').toString().toLowerCase().contains(
                    searchQuery,
                  ) ||
                  (item['barcode'] ?? '').toString().toLowerCase().contains(
                    searchQuery,
                  ) ||
                  (item['kategori'] ?? '').toString().toLowerCase().contains(
                    searchQuery,
                  ),
            )
            .toList();
      }
    });
  }

  void _cariDanTambahByBarcode(String code) {
    String kodeBersih = code.trim();
    if (kodeBersih.isEmpty) return;

    try {
      var hasilCari = daftarBarang.firstWhere(
        (item) => item['barcode'].toString() == kodeBersih,
        orElse: () => null,
      );

      if (hasilCari != null) {
        _tambahKeKeranjang(hasilCari);
        scanCtrl.clear();
        _showNotification(
          "${hasilCari['nama_barang']} ditambahkan!",
          Colors.green,
        );
      } else {
        _showNotification("Barcode $kodeBersih tidak ditemukan!", Colors.red);
        scanCtrl.clear();
      }
    } catch (e) {
      _showNotification('Error: $e', Colors.red);
    }
  }

  void _hitungTotal() {
    try {
      int subtotal = keranjang.fold(0, (sum, k) {
        int harga = _parseHarga(k['harga']);
        int qty = (k['qty'] is int)
            ? k['qty'] as int
            : int.tryParse(k['qty'].toString()) ?? 1;
        return sum + (harga * qty);
      });

      // Apply discount if any
      discountAmount = (subtotal * discountPercent / 100).toInt();
      totalBayar = subtotal - discountAmount;
    } catch (e) {
      print('Error menghitung total: $e');
      totalBayar = 0;
    }
  }

  void _applyPromoCode(String code) {
    code = code.toUpperCase().trim();

    // Sample promo codes
    Map<String, double> promos = {
      'DISKON10': 10.0,
      'DISKON20': 20.0,
      'DISKON50K': 50000.0, // Fixed amount
      'SPESIAL': 15.0,
    };

    if (promos.containsKey(code)) {
      setState(() {
        promoCode = code;

        // Check if it's a percentage or fixed amount discount
        if (code == 'DISKON50K') {
          discountPercent = 0.0;
          discountAmount = 50000;
          int subtotal = keranjang.fold(
            0,
            (sum, k) => sum + (_parseHarga(k['harga']) * (k['qty'] as int)),
          );
          totalBayar = (subtotal - discountAmount).toInt();
        } else {
          discountPercent = promos[code]!;
          _hitungTotal();
        }

        _showNotification('✓ Promo "$code" berhasil diterapkan!', Colors.green);
      });
    } else {
      _showNotification('❌ Kode promo tidak valid', Colors.red);
    }
  }

  void _resetDiscount() {
    setState(() {
      discountPercent = 0.0;
      discountAmount = 0;
      promoCode = "";
      _hitungTotal();
      _showNotification('Diskon dihapus', Colors.orange);
    });
  }

  void _kosongkanKeranjang() {
    setState(() {
      keranjang.clear();
      totalBayar = 0;
      discountPercent = 0.0;
      discountAmount = 0;
      promoCode = "";
    });
  }

  void _removeFromCart(int index) {
    setState(() {
      keranjang.removeAt(index);
      _hitungTotal();
    });
  }

  // ==== DIALOGS ====

  void _tampilkanFormTambah() {
    TextEditingController nCtrl = TextEditingController();
    TextEditingController kCtrl = TextEditingController();
    TextEditingController hCtrl = TextEditingController();
    TextEditingController sCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Tambah Barang Baru"),
        content: SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nCtrl,
                decoration: const InputDecoration(labelText: "Nama Barang"),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: kCtrl,
                decoration: const InputDecoration(labelText: "Kategori"),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: hCtrl,
                decoration: const InputDecoration(labelText: "Harga"),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: sCtrl,
                decoration: const InputDecoration(labelText: "Stok Awal"),
                keyboardType: TextInputType.number,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Batal"),
          ),
          ElevatedButton(
            onPressed: () => simpanBarangBaru(
              nCtrl.text,
              kCtrl.text,
              hCtrl.text,
              sCtrl.text,
            ),
            child: const Text("Simpan"),
          ),
        ],
      ),
    );
  }

  Future<void> _dialogRestok(int id, String namaBarang) async {
    TextEditingController jumlahController = TextEditingController();

    return showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text("Restok: $namaBarang"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text("Berapa banyak barang yang baru datang?"),
              const SizedBox(height: 15),
              TextField(
                controller: jumlahController,
                autofocus: true,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: "Jumlah",
                  hintText: "Contoh: 50",
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Batal"),
            ),
            ElevatedButton(
              onPressed: () {
                int jumlahInput = int.tryParse(jumlahController.text) ?? 0;
                if (jumlahInput > 0) {
                  prosesRestok(id, jumlahInput);
                  Navigator.pop(context);
                } else {
                  _showNotification(
                    "Masukkan jumlah yang valid!",
                    Colors.orange,
                  );
                }
              },
              child: const Text("Simpan Stok"),
            ),
          ],
        );
      },
    );
  }

  void _tampilkanRiwayat() async {
    await ambilLaporan();

    if (!mounted) return;

    showDialog(
      context: context,
      builder: (context) => Dialog(
        insetPadding: const EdgeInsets.all(16),
        child: Scaffold(
          appBar: AppBar(
            title: const Text("📊 Riwayat Transaksi Lengkap"),
            backgroundColor: Colors.indigo,
            foregroundColor: Colors.white,
            automaticallyImplyLeading: true,
          ),
          body: transactions.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.history, size: 64, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text(
                        "Tidak ada riwayat transaksi",
                        style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: transactions.length,
                  itemBuilder: (context, index) {
                    final transaction = transactions[index];
                    return Card(
                      elevation: 2,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: ExpansionTile(
                        leading: Icon(Icons.receipt_long, color: Colors.indigo),
                        title: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  transaction.transactionId,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                                Text(
                                  _formatDateTime(transaction.dateTime),
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  transaction.formattedFinalTotal,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                    color: Colors.green,
                                  ),
                                ),
                                if (transaction.discount > 0)
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 2,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.red[50],
                                      border: Border.all(
                                        color: Colors.red,
                                        width: 1,
                                      ),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      "-${transaction.discountPercent > 0 ? '${transaction.discountPercent.toStringAsFixed(0)}%' : transaction.formattedDiscount}",
                                      style: const TextStyle(
                                        fontSize: 10,
                                        color: Colors.red,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          ],
                        ),
                        children: [
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Items
                                const Text(
                                  "📦 Detail Barang:",
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Container(
                                  decoration: BoxDecoration(
                                    color: Colors.grey[50],
                                    border: Border.all(
                                      color: Colors.grey[300]!,
                                    ),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  padding: const EdgeInsets.all(12),
                                  child: transaction.items.isEmpty
                                      ? Center(
                                          child: Text(
                                            "Tidak ada item",
                                            style: TextStyle(
                                              color: Colors.grey[400],
                                              fontSize: 12,
                                            ),
                                          ),
                                        )
                                      : Column(
                                          children: transaction.items.map<Widget>((
                                            item,
                                          ) {
                                            try {
                                              int itemHarga = _parseHarga(
                                                item['harga'] ?? 0,
                                              );
                                              int itemQty = (item['qty'] is int)
                                                  ? item['qty'] as int
                                                  : int.tryParse(
                                                          item['qty']
                                                              .toString(),
                                                        ) ??
                                                        1;
                                              int itemTotal =
                                                  itemHarga * itemQty;
                                              String itemNama =
                                                  item['nama']?.toString() ??
                                                  "Unknown";

                                              return Padding(
                                                padding:
                                                    const EdgeInsets.symmetric(
                                                      vertical: 6,
                                                    ),
                                                child: Row(
                                                  mainAxisAlignment:
                                                      MainAxisAlignment
                                                          .spaceBetween,
                                                  children: [
                                                    Expanded(
                                                      child: Column(
                                                        crossAxisAlignment:
                                                            CrossAxisAlignment
                                                                .start,
                                                        children: [
                                                          Text(
                                                            itemNama,
                                                            style:
                                                                const TextStyle(
                                                                  fontWeight:
                                                                      FontWeight
                                                                          .bold,
                                                                  fontSize: 12,
                                                                ),
                                                            maxLines: 2,
                                                            overflow:
                                                                TextOverflow
                                                                    .ellipsis,
                                                          ),
                                                          Text(
                                                            "${itemQty}x @ Rp ${itemHarga.toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+(?!\d))'), (m) => '${m[1]}.')}",
                                                            style: TextStyle(
                                                              fontSize: 11,
                                                              color: Colors
                                                                  .grey[600],
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                    ),
                                                    Text(
                                                      "Rp ${itemTotal.toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+(?!\d))'), (m) => '${m[1]}.')}",
                                                      style: const TextStyle(
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        fontSize: 12,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              );
                                            } catch (e) {
                                              print('Error rendering item: $e');
                                              return const SizedBox.shrink();
                                            }
                                          }).toList(),
                                        ),
                                ),
                                const SizedBox(height: 16),
                                // Pricing Summary
                                const Divider(),
                                const SizedBox(height: 8),
                                _buildSummaryRow(
                                  "Subtotal:",
                                  transaction.formattedSubtotal,
                                  Colors.black,
                                ),
                                const SizedBox(height: 6),
                                if (transaction.discount > 0) ...[
                                  _buildSummaryRow(
                                    "Diskon${transaction.discountCode.isNotEmpty ? ' (${transaction.discountCode})' : ''}:",
                                    "- ${transaction.formattedDiscount}",
                                    Colors.red,
                                  ),
                                  const SizedBox(height: 6),
                                ],
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 6,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.indigo[50],
                                    border: Border.all(
                                      color: Colors.indigo,
                                      width: 2,
                                    ),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      const Text(
                                        "💰 Total Pembayaran:",
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13,
                                        ),
                                      ),
                                      Text(
                                        transaction.formattedFinalTotal,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 14,
                                          color: Colors.indigo,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value, Color textColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(fontSize: 12, color: textColor)),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 12,
            color: textColor,
          ),
        ),
      ],
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return "${dateTime.day.toString().padLeft(2, '0')}/${dateTime.month.toString().padLeft(2, '0')}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}";
  }

  // ==== HELPER FUNCTIONS ====

  void _showNotification(String pesan, Color warna) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(pesan),
        backgroundColor: warna,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  // ==== BUILD ====

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Sistem Kasir Toko Papa - Pro Edition"),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        elevation: 4,
      ),
      body: Row(
        children: [
          // ===== SIDEBAR =====
          Container(
            width: 250,
            color: Colors.grey[100],
            child: Column(
              children: [
                const UserAccountsDrawerHeader(
                  decoration: BoxDecoration(color: Colors.indigo),
                  accountName: Text("Admin Kasir"),
                  accountEmail: Text("Toko Elektronik Ayah"),
                  currentAccountPicture: CircleAvatar(
                    backgroundColor: Colors.white,
                    child: Icon(Icons.person, color: Colors.indigo),
                  ),
                ),
                ListTile(
                  leading: const Icon(
                    Icons.point_of_sale,
                    color: Colors.indigo,
                  ),
                  title: const Text("Kasir (POS)"),
                  selected: halamanAktif == 0,
                  onTap: () {
                    setState(() => halamanAktif = 0);
                    refreshData();
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.dashboard, color: Colors.indigo),
                  title: const Text("Dashboard"),
                  selected: halamanAktif == 1,
                  onTap: () {
                    setState(() => halamanAktif = 1);
                    refreshData();
                    ambilStats();
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.inventory_2, color: Colors.indigo),
                  title: const Text("Inventaris"),
                  selected: halamanAktif == 2,
                  onTap: () {
                    setState(() => halamanAktif = 2);
                    refreshData();
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.history, color: Colors.indigo),
                  title: const Text("Riwayat"),
                  onTap: _tampilkanRiwayat,
                ),
                const Spacer(),
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text(
                    "v2.0.0 Pro",
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
              ],
            ),
          ),

          // ===== MAIN CONTENT =====
          Expanded(child: _buildMainContent()),
        ],
      ),
    );
  }

  Widget _buildMainContent() {
    if (isLoading && daftarBarang.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    switch (halamanAktif) {
      case 0:
        return KasirScreen(
          daftarBarang: daftarBarangFiltered.isEmpty && daftarBarang.isNotEmpty
              ? daftarBarang
              : daftarBarangFiltered,
          keranjang: keranjang,
          totalBayar: totalBayar,
          discountAmount: discountAmount,
          discountPercent: discountPercent,
          promoCode: promoCode,
          isLoading: isLoading,
          scanCtrl: scanCtrl,
          onTambahKeKeranjang: _tambahKeKeranjang,
          onCariBarcode: _cariDanTambahByBarcode,
          onCariProduk: _cariProduk,
          onRemoveFromCart: _removeFromCart,
          onUpdateQty: _updateKeranjangQty,
          onApplyPromo: _applyPromoCode,
          onResetDiscount: _resetDiscount,
          onCheckout: prosesCheckout,
          onKosongkanKeranjang: _kosongkanKeranjang,
          onTambahBarang: _tampilkanFormTambah,
          onRestok: _dialogRestok,
        );
      case 1:
        return DashboardScreen(
          daftarBarang: daftarBarang,
          omzetHariIni: omzetHariIni,
          topProduk: topProduk,
          onRestok: _dialogRestok,
        );
      case 2:
        return InventarisScreen(
          daftarBarang: daftarBarang,
          onTambahBarang: _tampilkanFormTambah,
          onRestok: _dialogRestok,
        );
      default:
        return const Center(child: Text("Halaman tidak ditemukan"));
    }
  }
}
