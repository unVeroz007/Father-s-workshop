import 'package:flutter/material.dart';

/// Inventory/Stock Management Screen
class InventarisScreen extends StatelessWidget {
  final List<dynamic> daftarBarang;
  final VoidCallback onTambahBarang;
  final Function(int, String) onRestok;

  const InventarisScreen({
    Key? key,
    required this.daftarBarang,
    required this.onTambahBarang,
    required this.onRestok,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// HEADER
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "📝 Manajemen Inventaris",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              ElevatedButton.icon(
                onPressed: onTambahBarang,
                icon: const Icon(Icons.add),
                label: const Text("Tambah Barang"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.indigo,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 15,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          /// STATS
          Row(
            children: [
              _buildStatCard(
                "Total Produk",
                daftarBarang.length.toString(),
                Colors.blue,
                Icons.shopping_bag,
              ),
              const SizedBox(width: 20),
              _buildStatCard(
                "Stok Aman",
                _countSafeStock().toString(),
                Colors.green,
                Icons.check_circle,
              ),
              const SizedBox(width: 20),
              _buildStatCard(
                "Stok Rendah",
                _countLowStock().toString(),
                Colors.orange,
                Icons.warning,
              ),
              const SizedBox(width: 20),
              _buildStatCard(
                "Stok Habis",
                _countOutOfStock().toString(),
                Colors.red,
                Icons.error,
              ),
            ],
          ),
          const SizedBox(height: 24),

          /// TABLE
          Expanded(
            child: Card(
              elevation: 3,
              child: SingleChildScrollView(
                child: SizedBox(
                  width: double.infinity,
                  child: DataTable(
                    headingRowColor: MaterialStateProperty.all(
                      Colors.indigo[50],
                    ),
                    columns: const [
                      DataColumn(
                        label: Text(
                          "No",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataColumn(
                        label: Text(
                          "Nama Barang",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataColumn(
                        label: Text(
                          "Kategori",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataColumn(
                        label: Text(
                          "Harga",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataColumn(
                        label: Text(
                          "Stok",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataColumn(
                        label: Text(
                          "Status",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataColumn(
                        label: Text(
                          "Aksi",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                    rows: daftarBarang.asMap().entries.map((entry) {
                      int index = entry.key + 1;
                      var item = entry.value;

                      int stok =
                          int.tryParse(
                            item['stok_tersedia']?.toString() ??
                                item['stok']?.toString() ??
                                '0',
                          ) ??
                          0;

                      String status = stok == 0
                          ? "Habis"
                          : stok <= 5
                          ? "Rendah"
                          : "Aman";

                      Color statusColor = stok == 0
                          ? Colors.red
                          : stok <= 5
                          ? Colors.orange
                          : Colors.green;

                      return DataRow(
                        cells: [
                          DataCell(Text(index.toString())),
                          DataCell(
                            Text(
                              item['nama_barang'] ?? "N/A",
                              style: const TextStyle(
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                          DataCell(
                            Chip(
                              label: Text(item['kategori'] ?? "Umum"),
                              backgroundColor: Colors.indigo[100],
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
                              stok.toString(),
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: statusColor,
                              ),
                            ),
                          ),
                          DataCell(
                            Chip(
                              label: Text(status),
                              backgroundColor: statusColor.withOpacity(0.2),
                              labelStyle: TextStyle(
                                color: statusColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          DataCell(
                            Row(
                              children: [
                                ElevatedButton(
                                  onPressed: () =>
                                      onRestok(item['id'], item['nama_barang']),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 12,
                                      vertical: 8,
                                    ),
                                  ),
                                  child: const Text("Restok"),
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
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    Color color,
    IconData icon,
  ) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color, width: 2),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }

  int _countSafeStock() {
    return daftarBarang.where((item) {
      int stok =
          int.tryParse(
            item['stok_tersedia']?.toString() ??
                item['stok']?.toString() ??
                '0',
          ) ??
          0;
      return stok > 5;
    }).length;
  }

  int _countLowStock() {
    return daftarBarang.where((item) {
      int stok =
          int.tryParse(
            item['stok_tersedia']?.toString() ??
                item['stok']?.toString() ??
                '0',
          ) ??
          0;
      return stok > 0 && stok <= 5;
    }).length;
  }

  int _countOutOfStock() {
    return daftarBarang.where((item) {
      int stok =
          int.tryParse(
            item['stok_tersedia']?.toString() ??
                item['stok']?.toString() ??
                '0',
          ) ??
          0;
      return stok == 0;
    }).length;
  }
}
