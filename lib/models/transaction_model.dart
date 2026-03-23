class Transaction {
  final int id;
  final String transactionId;
  final List<Map<String, dynamic>> items;
  final int subtotal;
  final int discount;
  final double discountPercent;
  final String discountCode;
  final int finalTotal;
  final DateTime dateTime;
  final String paymentStatus;

  Transaction({
    required this.id,
    required this.transactionId,
    required this.items,
    required this.subtotal,
    required this.discount,
    required this.discountPercent,
    required this.discountCode,
    required this.finalTotal,
    required this.dateTime,
    required this.paymentStatus,
  });

  // Format currency to Rp format
  String get formattedSubtotal =>
      'Rp ${subtotal.toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+(?!\d))'), (m) => '${m[1]}.')}';
  String get formattedDiscount =>
      'Rp ${discount.toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+(?!\d))'), (m) => '${m[1]}.')}';
  String get formattedFinalTotal =>
      'Rp ${finalTotal.toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+(?!\d))'), (m) => '${m[1]}.')}';

  // Factory untuk membuat dari JSON Laravel
  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] ?? 0,
      transactionId: json['transaction_id'] ?? 'TRX-${json['id']}',
      items: _parseItems(json['items']),
      subtotal: json['subtotal'] ?? 0,
      discount: json['discount'] ?? 0,
      discountPercent: (json['discount_percent'] ?? 0).toDouble(),
      discountCode: json['discount_code'] ?? '',
      finalTotal: json['final_total'] ?? json['total_amount'] ?? 0,
      dateTime: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      paymentStatus: json['payment_status'] ?? 'success',
    );
  }

  static List<Map<String, dynamic>> _parseItems(dynamic items) {
    if (items == null) return [];
    if (items is List) {
      return items.cast<Map<String, dynamic>>();
    }
    return [];
  }
}
