import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/product_model.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';

  // Fungsi ambil semua barang
  static Future<List<Product>> getProducts() async {
    final res = await http.get(Uri.parse('$baseUrl/cek-barang'));
    if (res.statusCode == 200) {
      List data = jsonDecode(res.body);
      return data.map((item) => Product.fromJson(item)).toList();
    }
    throw Exception("Gagal memuat data barang");
  }

  // Fungsi Checkout
  static Future<bool> checkout(List<Map<String, dynamic>> items) async {
    final res = await http.post(
      Uri.parse('$baseUrl/checkout'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'items': items}),
    );
    return res.statusCode == 200;
  }
}