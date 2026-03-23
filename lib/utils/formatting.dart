/// Utility functions untuk formatting data
class FormatUtils {
  /// Format integer menjadi currency (Rp format dengan separator)
  /// Example: 25000 → "Rp 25.000"
  static String formatCurrency(int amount) {
    if (amount < 0) return "Rp 0";

    String formatted = amount.toString();
    StringBuffer buffer = StringBuffer();

    int counter = 0;
    for (int i = formatted.length - 1; i >= 0; i--) {
      if (counter > 0 && counter % 3 == 0) {
        buffer.write('.');
      }
      buffer.write(formatted[i]);
      counter++;
    }

    return "Rp ${buffer.toString().split('').reversed.join('')}";
  }

  /// Parse currency string ke integer
  /// Example: "Rp 25.000" → 25000
  static int parseCurrency(String value) {
    return int.tryParse(value.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
  }

  /// Format tanggal ke format lokal (DD/MM/YYYY)
  static String formatDate(String? dateStr) {
    if (dateStr == null || dateStr.isEmpty) return "N/A";
    try {
      DateTime date = DateTime.parse(dateStr);
      return "${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}";
    } catch (e) {
      return dateStr;
    }
  }

  /// Format jam ke format lokal (HH:MM:SS)
  static String formatTime(String? dateStr) {
    if (dateStr == null || dateStr.isEmpty) return "N/A";
    try {
      DateTime date = DateTime.parse(dateStr);
      return "${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}:${date.second.toString().padLeft(2, '0')}";
    } catch (e) {
      return dateStr;
    }
  }

  /// Format datetime lengkap
  static String formatDateTime(String? dateStr) {
    if (dateStr == null || dateStr.isEmpty) return "N/A";
    return "${formatDate(dateStr)} ${formatTime(dateStr)}";
  }

  /// Format persentase
  static String formatPercent(double percent) {
    return "${percent.toStringAsFixed(2)}%";
  }

  /// Format angka dengan decimal
  static String formatNumber(double number, {int decimals = 2}) {
    return number.toStringAsFixed(decimals);
  }

  /// Abbreviate large numbers (e.g., 1500 → "1.5K")
  static String abbreviateNumber(int number) {
    if (number < 1000) return number.toString();
    if (number < 1000000) return "${(number / 1000).toStringAsFixed(1)}K";
    if (number < 1000000000) return "${(number / 1000000).toStringAsFixed(1)}M";
    return "${(number / 1000000000).toStringAsFixed(1)}B";
  }
}
