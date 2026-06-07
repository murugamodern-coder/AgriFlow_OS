import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/features/billing/domain/models/billing_models.dart';
import 'package:dio/dio.dart';

/// Billing APIs return raw Frappe `message` payloads (not the mobile ApiEnvelope).
class BillingRepository {
  BillingRepository({required Dio dio, required ApiConfig config})
      : _dio = dio,
        _config = config;

  final Dio _dio;
  final ApiConfig _config;

  Future<List<CatalogItem>> searchItems({String search = '', int limit = 20}) async {
    final response = await _dio.get<dynamic>(
      _config.methodUrl('agriflow.api.v1.billing.get_item_search'),
      queryParameters: {'search': search, 'limit': limit},
    );
    final data = response.data['message'] as List<dynamic>;
    return data
        .map((j) => CatalogItem.fromJson(Map<String, dynamic>.from(j as Map)))
        .toList();
  }

  Future<InvoiceResult> createCashCarryInvoice({
    required List<CartLine> items,
    String customerName = '',
    String customerMobile = '',
    PaymentMode paymentMode = PaymentMode.cash,
  }) async {
    final response = await _dio.post<dynamic>(
      _config.methodUrl('agriflow.api.v1.billing.create_cash_carry_invoice'),
      data: {
        'items': items.map((c) => c.toApiPayload()).toList(),
        'customer_name': customerName,
        'customer_mobile': customerMobile,
        'payment_mode': paymentMode.apiValue,
      },
    );
    final data = Map<String, dynamic>.from(response.data['message'] as Map);
    return InvoiceResult.fromJson(data);
  }

  Future<List<Map<String, dynamic>>> recentInvoices({
    int limit = 20,
    String? saleMode,
  }) async {
    final params = <String, dynamic>{'limit': limit};
    if (saleMode != null) params['sale_mode'] = saleMode;

    final response = await _dio.get<dynamic>(
      _config.methodUrl('agriflow.api.v1.billing.list_recent_invoices'),
      queryParameters: params,
    );
    return (response.data['message'] as List<dynamic>)
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();
  }
}
