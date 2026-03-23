import 'package:flutter/material.dart';

/// Kasir/POS Screen - For selling products
class KasirScreen extends StatelessWidget {
  final List<dynamic> daftarBarang;
  final List<dynamic> keranjang;
  final int totalBayar;
  final int discountAmount;
  final double discountPercent;
  final String promoCode;
  final bool isLoading;
  final TextEditingController scanCtrl;
  final Function(Map<dynamic, dynamic>) onTambahKeKeranjang;
  final Function(String) onCariBarcode;
  final Function(String) onCariProduk;
  final Function(int) onRemoveFromCart;
  final Function(int, int) onUpdateQty;
  final Function(String) onApplyPromo;
  final VoidCallback onResetDiscount;
  final VoidCallback onCheckout;
  final VoidCallback onKosongkanKeranjang;
  final VoidCallback onTambahBarang;
  final Function(int, String) onRestok;

  const KasirScreen({
    Key? key,
    required this.daftarBarang,
    required this.keranjang,
    required this.totalBayar,
    required this.discountAmount,
    required this.discountPercent,
    required this.promoCode,
    required this.isLoading,
    required this.scanCtrl,
    required this.onTambahKeKeranjang,
    required this.onCariBarcode,
    required this.onCariProduk,
    required this.onRemoveFromCart,
    required this.onUpdateQty,
    required this.onApplyPromo,
    required this.onResetDiscount,
    required this.onCheckout,
    required this.onKosongkanKeranjang,
    required this.onTambahBarang,
    required this.onRestok,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        /// ===== LEFT SIDE: PRODUCTS LIST =====
        Expanded(
          flex: 3,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                /// HEADER
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      "📦 Daftar Produk",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: onTambahBarang,
                      icon: const Icon(Icons.add),
                      label: const Text("Barang Baru"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.indigo,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 12,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                /// BARCODE SCANNER
                TextField(
                  controller: scanCtrl,
                  autofocus: true,
                  decoration: InputDecoration(
                    labelText: "Scan Barcode atau Ketik di sini",
                    hintText: "Gunakan barcode scanner + Enter",
                    prefixIcon: const Icon(
                      Icons.qr_code_scanner,
                      color: Colors.indigo,
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  onSubmitted: onCariBarcode,
                ),
                const SizedBox(height: 12),

                /// PRODUCT SEARCH
                TextField(
                  decoration: InputDecoration(
                    labelText: "🔍 Cari Produk (Nama/Barcode/Kategori)",
                    hintText: "Ketik untuk mencari...",
                    prefixIcon: const Icon(Icons.search, color: Colors.indigo),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  onChanged: onCariProduk,
                ),
                const SizedBox(height: 16),

                /// PRODUCTS TABLE
                Expanded(
                  child: Card(
                    elevation: 3,
                    child: isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : SingleChildScrollView(
                            child: SizedBox(
                              width: double.infinity,
                              child: DataTable(
                                headingRowColor: MaterialStateProperty.all(
                                  Colors.indigo[50],
                                ),
                                columns: const [
                                  DataColumn(
                                    label: Text(
                                      "Nama Barang",
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  DataColumn(
                                    label: Text(
                                      "Harga",
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  DataColumn(
                                    label: Text(
                                      "Stok",
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  DataColumn(
                                    label: Text(
                                      "Aksi",
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ],
                                rows: daftarBarang.map((item) {
                                  return DataRow(
                                    cells: [
                                      DataCell(
                                        Text(
                                          item['nama_barang'] ?? "N/A",
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                      ),
                                      DataCell(
                                        Text(
                                          "Rp ${item['harga'] ?? '0'}",
                                          style: const TextStyle(
                                            color: Colors.green,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      DataCell(
                                        Text(
                                          "${item['stok_tersedia'] ?? item['stok'] ?? '0'}",
                                        ),
                                      ),
                                      DataCell(
                                        Row(
                                          children: [
                                            IconButton(
                                              tooltip: "Tambah ke Keranjang",
                                              icon: const Icon(
                                                Icons.add_shopping_cart,
                                                color: Colors.blue,
                                              ),
                                              onPressed: () =>
                                                  onTambahKeKeranjang(item),
                                            ),
                                            IconButton(
                                              tooltip: "Restok",
                                              icon: const Icon(
                                                Icons.add_box,
                                                color: Colors.green,
                                              ),
                                              onPressed: () => onRestok(
                                                item['id'],
                                                item['nama_barang'],
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  );
                                }).toList(),
                              ),
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(width: 24),

        /// ===== RIGHT SIDE: RECEIPT/CHECKOUT =====
        Container(
          width: 380,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(15),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.15),
                blurRadius: 10,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Column(
            children: [
              /// HEADER
              Container(
                padding: const EdgeInsets.all(16),
                decoration: const BoxDecoration(
                  color: Colors.indigo,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(15),
                    topRight: Radius.circular(15),
                  ),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.receipt_long, color: Colors.white),
                    SizedBox(width: 12),
                    Text(
                      "🧾 Struk Pembayaran",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

              /// CART ITEMS
              Expanded(
                child: keranjang.isEmpty
                    ? const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.shopping_cart_outlined,
                              size: 48,
                              color: Colors.grey,
                            ),
                            SizedBox(height: 12),
                            Text(
                              "Keranjang Kosong",
                              style: TextStyle(
                                color: Colors.grey,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: keranjang.length,
                        itemBuilder: (context, index) {
                          final item = keranjang[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 6),
                            child: Column(
                              children: [
                                ListTile(
                                  dense: true,
                                  title: Text(
                                    item['nama'],
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Text(
                                    "Rp ${item['harga']} × ${item['qty']} = Rp ${item['harga'] * item['qty']}",
                                    style: const TextStyle(
                                      color: Colors.green,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                                Padding(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 8,
                                  ),
                                  child: Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          IconButton(
                                            icon: const Icon(
                                              Icons.remove_circle,
                                              color: Colors.orange,
                                              size: 20,
                                            ),
                                            onPressed: () => onUpdateQty(
                                              index,
                                              item['qty'] - 1,
                                            ),
                                            padding: EdgeInsets.zero,
                                            constraints: const BoxConstraints(),
                                          ),
                                          Padding(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 8,
                                            ),
                                            child: Text(
                                              "${item['qty']}",
                                              style: const TextStyle(
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                          ),
                                          IconButton(
                                            icon: const Icon(
                                              Icons.add_circle,
                                              color: Colors.green,
                                              size: 20,
                                            ),
                                            onPressed: () => onUpdateQty(
                                              index,
                                              item['qty'] + 1,
                                            ),
                                            padding: EdgeInsets.zero,
                                            constraints: const BoxConstraints(),
                                          ),
                                        ],
                                      ),
                                      IconButton(
                                        icon: const Icon(
                                          Icons.delete_outline,
                                          color: Colors.red,
                                          size: 20,
                                        ),
                                        onPressed: () =>
                                            onRemoveFromCart(index),
                                        padding: EdgeInsets.zero,
                                        constraints: const BoxConstraints(),
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

              const Divider(height: 1),

              /// PROMO CODE SECTION
              if (keranjang.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                  child: Column(
                    children: [
                      if (promoCode.isNotEmpty)
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.green[50],
                            border: Border.all(color: Colors.green),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                "✓ Promo: $promoCode ($discountPercent% OFF)",
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.close, size: 16),
                                onPressed: onResetDiscount,
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                              ),
                            ],
                          ),
                        )
                      else
                        TextField(
                          decoration: InputDecoration(
                            labelText: "Kode Promo (Opsional)",
                            hintText: "Cth: DISKON10",
                            prefixIcon: const Icon(Icons.local_offer),
                            suffixIcon: IconButton(
                              icon: const Icon(Icons.check),
                              onPressed: () {
                                // Get the value from a temporary controller
                                // For now, we'll just show the hint
                              },
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                          ),
                          onSubmitted: onApplyPromo,
                        ),
                    ],
                  ),
                ),

              /// TOTAL & CHECKOUT
              Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    if (discountAmount > 0)
                      Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                "Subtotal:",
                                style: TextStyle(fontSize: 14),
                              ),
                              Text(
                                "Rp ${totalBayar + discountAmount}",
                                style: const TextStyle(fontSize: 14),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                "Diskon:",
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.red,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                "- Rp $discountAmount",
                                style: const TextStyle(
                                  fontSize: 14,
                                  color: Colors.red,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const Divider(),
                          const SizedBox(height: 6),
                        ],
                      ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          "TOTAL:",
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          "Rp $totalBayar",
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        onPressed: keranjang.isEmpty ? null : onCheckout,
                        child: const Text(
                          "💰 PROSES BAYAR",
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    if (keranjang.isNotEmpty)
                      TextButton(
                        onPressed: onKosongkanKeranjang,
                        child: const Text(
                          "Kosongkan Keranjang",
                          style: TextStyle(color: Colors.red),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 16),
      ],
    );
  }
}
