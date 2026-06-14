import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../domain/officer_model.dart';
import '../providers/officer_provider.dart';

/// Screen showing government officers with workload and call action.
class OfficerListScreen extends ConsumerWidget {
  const OfficerListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final officersAsync = ref.watch(officersListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Officers / அதிகாரிகள்'),
        backgroundColor: Colors.indigo.shade700,
        foregroundColor: Colors.white,
      ),
      body: officersAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 12),
                Text('Error: $e', textAlign: TextAlign.center),
                const SizedBox(height: 12),
                ElevatedButton(
                  onPressed: () => ref.invalidate(officersListProvider),
                  child: const Text('Retry / மீண்டும்'),
                ),
              ],
            ),
          ),
        ),
        data: (officers) {
          if (officers.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.account_balance,
                      size: 64,
                      color: Colors.indigo.shade200,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'No officers / அதிகாரிகள் இல்லை',
                      style: TextStyle(fontSize: 16),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(officersListProvider),
            child: ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: officers.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, i) =>
                  _OfficerCard(officer: officers[i]),
            ),
          );
        },
      ),
    );
  }
}

class _OfficerCard extends StatelessWidget {
  const _OfficerCard({required this.officer});

  final GovernmentOfficer officer;

  Future<void> _call(String mobile) async {
    final uri = Uri(scheme: 'tel', path: mobile);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: Colors.indigo.shade100,
              child: Text(
                officer.officerName.isNotEmpty
                    ? officer.officerName[0]
                    : '?',
                style: TextStyle(color: Colors.indigo.shade900),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    officer.officerName,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    officer.designation,
                    style: TextStyle(
                      color: Colors.grey.shade700,
                      fontSize: 12,
                    ),
                  ),
                  if (officer.officeLocation != null)
                    Text(
                      officer.officeLocation!,
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 11,
                      ),
                    ),
                  Row(
                    children: [
                      Icon(
                        Icons.work,
                        size: 12,
                        color: Colors.indigo.shade400,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${officer.activeProjects} active projects',
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.indigo.shade700,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            IconButton(
              icon: Icon(Icons.phone, color: Colors.green.shade700),
              onPressed: () => _call(officer.mobile),
            ),
          ],
        ),
      ),
    );
  }
}