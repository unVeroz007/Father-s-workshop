class Barang {
  final int id;
  final String nama;
  final int harga;
  final int stok;
  final String? barcode;

  Barang({required this.id, required this.nama, required this.harga, required this.stok, this.barcode});

  // Mengubah JSON dari Laravel menjadi Objek Dart (PBO)
  factory Barang.fromJson(Map<String, dynamic> json) {
    return Barang(
      id: json['id'],
      nama: json['nama_barang'],
      harga: int.parse(json['harga'].toString()),
      stok: int.parse((json['stok_tersedia'] ?? json['stok'] ?? 0).toString()),
      barcode: json['barcode'],
    );
  }
}