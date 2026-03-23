class Product {
  final int id;
  final String nama;
  final String kategori;
  final int harga;
  int stok;

  Product({
    required this.id,
    required this.nama,
    required this.kategori,
    required this.harga,
    required this.stok,
  });

  // Fungsi sakti untuk mengubah JSON dari Laravel menjadi Objek Dart
  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      nama: json['nama_barang'],
      kategori: json['kategori'] ?? 'Umum',
      harga: int.parse(json['harga'].toString()),
      stok: int.parse((json['stok_tersedia'] ?? json['stok'] ?? 0).toString()),
    );
  }
}