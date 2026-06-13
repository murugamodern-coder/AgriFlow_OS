import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class PrintService {
  Future<File> _savePdfToTemp({
    required String filename,
    required String base64Pdf,
  }) async {
    final bytes = base64Decode(base64Pdf);
    final tempDir = await getTemporaryDirectory();
    final file = File('${tempDir.path}/$filename');
    await file.writeAsBytes(bytes, flush: true);
    return file;
  }

  Future<void> shareInvoicePdf({
    required String filename,
    required String base64Pdf,
    String? subject,
  }) async {
    final file = await _savePdfToTemp(filename: filename, base64Pdf: base64Pdf);
    await Share.shareXFiles(
      [XFile(file.path)],
      subject: subject ?? 'Invoice $filename',
      text: 'AgriFlow Invoice - $filename',
    );
  }
}