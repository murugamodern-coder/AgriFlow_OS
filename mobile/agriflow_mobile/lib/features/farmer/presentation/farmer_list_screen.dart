import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/demo/demo_selection.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/features/farmer/data/farmer_remote.dart';
import 'package:agriflow_mobile/features/farmer/domain/farmer_summary.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/error_view.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final farmerListProvider = FutureProvider<List<FarmerSummary>>((ref) async {
  try {
    return await ref.read(farmerRemoteProvider).list();
  } catch (_) {
    return _farmersFromProjectCache(ref);
  }
});

Future<List<FarmerSummary>> _farmersFromProjectCache(Ref ref) async {
  final db = ref.read(appDatabaseProvider);
  final blocks = ref.read(hiveStorageProvider).getAllowedBlocks();
  final rows = await db.readProjections(
    kind: ProjectionKind.farmerProject,
    blocks: blocks,
  );
  final seen = <String>{};
  final out = <FarmerSummary>[];
  for (final row in rows) {
    final farmer = row.payload['farmer'] as String? ?? '';
    if (farmer.isEmpty || seen.contains(farmer)) continue;
    seen.add(farmer);
    final title = row.payload['project_title'] as String? ?? farmer;
    out.add(
      FarmerSummary(
        name: farmer,
        farmerName: title.split(' - ').first,
        block: row.payload['block'] as String?,
        village: row.payload['village'] as String?,
      ),
    );
  }
  return out;
}

class FarmerListScreen extends ConsumerWidget {
  const FarmerListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final farmers = ref.watch(farmerListProvider);

    return farmers.when(
      loading: () => const LoadingView(),
      error: (e, _) => ErrorView(
        onRetry: () => ref.invalidate(farmerListProvider),
      ),
      data: (items) {
        if (items.isEmpty) {
          return EmptyState(message: l10n.emptyFarmers);
        }
        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(farmerListProvider);
            await ref.read(syncOrchestratorProvider).syncNow();
          },
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final farmer = items[index];
              return Card(
                child: ListTile(
                  title: Text(farmer.farmerName),
                  subtitle: Text(
                    [
                      farmer.name,
                      if (farmer.village != null) farmer.village!,
                      if (farmer.mobile != null) farmer.mobile!,
                    ].join(' · '),
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _openProjectForFarmer(context, ref, farmer.name),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Future<void> _openProjectForFarmer(
    BuildContext context,
    WidgetRef ref,
    String farmerName,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    final db = ref.read(appDatabaseProvider);
    final blocks = ref.read(hiveStorageProvider).getAllowedBlocks();
    final rows = await db.readProjections(
      kind: ProjectionKind.farmerProject,
      blocks: blocks,
    );
    String? project;
    for (final row in rows) {
      if (row.payload['farmer'] == farmerName) {
        project = row.name;
        break;
      }
    }
    if (project == null) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.noProjectForFarmer)),
        );
      }
      return;
    }
    ref.read(selectedProjectProvider.notifier).state = project;
    if (context.mounted) {
      context.push(AppRoutes.projectTimeline(project));
    }
  }
}
