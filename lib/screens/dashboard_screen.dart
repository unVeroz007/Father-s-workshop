import 'package:flutter/material.dart';

/// Dashboard Analytics Screen - Menampilkan ringkasan penjualan dan inventaris
class DashboardScreen extends StatelessWidget {
  final List<dynamic> daftarBarang;
  final int omzetHariIni;
  final List<dynamic> topProduk;
  final Function(int, String) onRestok;

  const DashboardScreen({
    Key? key,
    required this.daftarBarang,
    required this.omzetHariIni,
    required this.topProduk,
    required this.onRestok,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Filter barang dengan stok kritis (0-5)
    List<dynamic> barangKritis = daftarBarang.where((item) {
      int stok =
          int.tryParse(
            item['stok_tersedia']?.toString() ??
                item['stok']?.toString() ??
                '999',
          ) ??
          999;
      return stok >= 0 && stok <= 5;
    }).toList();

    // Hitung total aset dari stok
    int totalAset = daftarBarang.fold(0, (sum, item) {
      num hrg =
          num.tryParse(
            item['harga']?.toString() ?? item['Harga']?.toString() ?? '0',
          ) ??
          0;
      num stk =
          num.tryParse(
            item['stok_tersedia']?.toString() ??
                item['stok']?.toString() ??
                item['Stok']?.toString() ??
                '0',
          ) ??
          0;
      return sum + (hrg.toInt() * stk.toInt());
    });

    return Padding(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// HEADER
          const Text(
            "📊 Dashboard Analitik Toko",
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),

          /// KPI CARDS
          Row(
            children: [
              _buildInfoCard(
                "Total Omzet",
                "Rp $omzetHariIni",
                Colors.orange,
                Icons.trending_up,
              ),
              const SizedBox(width: 20),
              _buildInfoCard(
                "Nilai Aset Stok",
                "Rp $totalAset",
                Colors.green,
                Icons.inventory_2,
              ),
              const SizedBox(width: 20),
              _buildInfoCard(
                "Stok Kritis",
                "${barangKritis.length} Item",
                Colors.red,
                Icons.warning,
              ),
            ],
          ),
          const SizedBox(height: 30),

          /// TOP 5 PRODUCTS
          const Text(
            "🔥 5 Produk Terlaris",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const Divider(),
          Expanded(
            child: topProduk.isEmpty
                ? const Center(child: Text("Belum ada data penjualan"))
                : ListView.builder(
                    itemCount: topProduk.length,
                    itemBuilder: (context, index) {
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.indigo,
                          foregroundColor: Colors.white,
                          child: Text("${index + 1}"),
                        ),
                        title: Text(
                          topProduk[index]['nama_barang'] ?? "Unknown",
                        ),
                        trailing: Text(
                          "${topProduk[index]['total_terjual'] ?? 0} Unit",
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo,
                          ),
                        ),
                      );
                    },
                  ),
          ),
          const SizedBox(height: 30),

          /// CRITICAL STOCK WARNING
          const Text(
            "⚠️ PERINGATAN: Stok Hampir Habis (< 5 Unit)",
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.red,
            ),
          ),
          const Divider(),
          Expanded(
            child: barangKritis.isEmpty
                ? const Center(
                    child: Text(
                      "Semua stok aman! Bos bisa tidur tenang. 😴",
                      style: TextStyle(fontSize: 18),
                    ),
                  )
                : ListView.builder(
                    itemCount: barangKritis.length,
                    itemBuilder: (context, index) {
                      var item = barangKritis[index];
                      int stok =
                          int.tryParse(
                            item['stok_tersedia']?.toString() ??
                                item['stok']?.toString() ??
                                '0',
                          ) ??
                          0;
                      return Card(
                        color: Colors.red[50],
                        margin: const EdgeInsets.symmetric(vertical: 8),
                        child: ListTile(
                          leading: const Icon(Icons.warning, color: Colors.red),
                          title: Text(
                            item['nama_barang'] ?? "Unknown",
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Text(
                            "Sisa Stok: $stok unit",
                            style: const TextStyle(
                              color: Colors.red,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          trailing: ElevatedButton(
                            onPressed: () =>
                                onRestok(item['id'], item['nama_barang']),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              foregroundColor: Colors.white,
                            ),
                            child: const Text("RESTOK"),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  /// Helper widget untuk KPI card
  static Widget _buildInfoCard(
    String title,
    String value,
    Color color,
    IconData icon,
  ) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color, width: 2),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.2),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const SizedBox(width: 10),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
