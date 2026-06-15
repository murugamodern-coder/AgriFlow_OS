import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/profit_provider.dart';

class ProfitDashboardScreen extends ConsumerWidget {
  const ProfitDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(dashboardSummaryProvider);
    final funnelAsync = ref.watch(workflowFunnelProvider);
    final schemesAsync = ref.watch(schemePerformanceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard / டாஷ்போர்டு'),
        backgroundColor: Colors.deepPurple.shade700,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(dashboardSummaryProvider);
          ref.invalidate(workflowFunnelProvider);
          ref.invalidate(schemePerformanceProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(12),
          children: [
            // KPI Cards
            summaryAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Error: $e'),
              data: (data) => _buildKpiSection(data),
            ),
            const SizedBox(height: 20),

            // Workflow Funnel
            const Text('Project Funnel / திட்ட நிலை',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            funnelAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Error: $e'),
              data: (stages) => _buildFunnel(stages),
            ),
            const SizedBox(height: 20),

            // Scheme Performance
            const Text('Scheme Performance / திட்ட செயல்பாடு',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            schemesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Error: $e'),
              data: (schemes) => _buildSchemes(schemes),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKpiSection(Map<String, dynamic> data) {
    final totals = (data['totals'] as Map<String, dynamic>?) ?? {};
    final monthRevenue = (data['month_to_date'] as Map<String, dynamic>?)?['revenue'] ?? 0;
    final today = (data['today'] as Map<String, dynamic>?) ?? {};

    return Column(
      children: [
        Row(
          children: [
            _kpiCard('Farmers', '${totals['farmers'] ?? 0}', Icons.people, Colors.green),
            const SizedBox(width: 8),
            _kpiCard('Projects', '${totals['projects'] ?? 0}', Icons.assignment, Colors.blue),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            _kpiCard('Active', '${totals['active_projects'] ?? 0}', Icons.trending_up, Colors.orange),
            const SizedBox(width: 8),
            _kpiCard('Visits Pending', '${totals['pending_visits'] ?? 0}', Icons.build, Colors.red),
          ],
        ),
        const SizedBox(height: 8),
        Card(
          color: Colors.deepPurple.shade50,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Month Revenue / மாத வருமானம்',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(
                  '₹${monthRevenue.toStringAsFixed(0)}',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple.shade700,
                  ),
                ),
                Text('Today: ${today['invoice_count'] ?? 0} invoices'),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _kpiCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 4),
              Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text(label, style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFunnel(List<dynamic> stages) {
    if (stages.isEmpty) return const Text('No data');
    final maxCount = stages.fold<int>(0, (m, s) {
      final c = (s as Map<String, dynamic>)['count'];
      final cInt = c is int ? c : int.tryParse('$c') ?? 0;
      return cInt > m ? cInt : m;
    });

    return Column(
      children: stages.map((s) {
        final stage = s as Map<String, dynamic>;
        final count = stage['count'] is int ? stage['count'] as int : int.tryParse('${stage['count']}') ?? 0;
        final ratio = maxCount > 0 ? count / maxCount : 0.0;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text('${stage['stage']}',
                        style: const TextStyle(fontSize: 13),
                        overflow: TextOverflow.ellipsis),
                  ),
                  Text('$count', style: const TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 4),
              LinearProgressIndicator(
                value: ratio,
                backgroundColor: Colors.grey.shade200,
                color: Colors.deepPurple.shade400,
                minHeight: 8,
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSchemes(List<dynamic> schemes) {
    if (schemes.isEmpty) return const Text('No scheme data');
    return Column(
      children: schemes.map((s) {
        final scheme = s as Map<String, dynamic>;
        return Card(
          child: ListTile(
            title: Text(scheme['scheme_type'] ?? '-'),
            subtitle: Text('${scheme['project_count']} projects | Avg ₹${(scheme['avg_value'] as num).toStringAsFixed(0)}'),
            trailing: Text(
              '₹${(scheme['total_value'] as num).toStringAsFixed(0)}',
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green),
            ),
          ),
        );
      }).toList(),
    );
  }
}