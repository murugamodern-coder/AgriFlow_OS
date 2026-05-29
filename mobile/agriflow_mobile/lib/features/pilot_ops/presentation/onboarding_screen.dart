import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/features/pilot_ops/data/pilot_ops_remote.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

const pilotOnboardingDoneKey = 'pilot_onboarding_done';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  List<Map<String, dynamic>> _steps = [];
  final Set<String> _checked = {};
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final steps = await ref.read(pilotOpsRemoteProvider).fetchOnboardingSteps();
      if (mounted) {
        setState(() {
          _steps = steps;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _labelForStep(AppLocalizations l10n, String id) {
    switch (id) {
      case 'login':
        return l10n.onboardingLogin;
      case 'sync_initial':
        return l10n.onboardingInitialSync;
      case 'review_tasks':
        return l10n.onboardingReviewTasks;
      case 'offline_test':
        return l10n.onboardingOfflineTest;
      case 'feedback_channel':
        return l10n.onboardingFeedback;
      default:
        return id;
    }
  }

  Future<void> _complete() async {
    await ref.read(hiveStorageProvider).box(HiveBoxNames.appPrefs).put(pilotOnboardingDoneKey, true);
    if (mounted) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: Text(l10n.onboardingTitle)),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    return Scaffold(
      appBar: AppBar(title: Text(l10n.onboardingTitle)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(l10n.onboardingIntro, style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 16),
          ..._steps.map((step) {
            final id = step['id']?.toString() ?? '';
            final required = step['required'] == true;
            return CheckboxListTile(
              value: _checked.contains(id),
              onChanged: (v) {
                setState(() {
                  if (v == true) {
                    _checked.add(id);
                  } else {
                    _checked.remove(id);
                  }
                });
              },
              title: Text(_labelForStep(l10n, id)),
              subtitle: required ? Text(l10n.onboardingRequired) : null,
            );
          }),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _complete,
            child: Text(l10n.onboardingDone),
          ),
        ],
      ),
    );
  }
}

/// Returns true if onboarding should be shown (first pilot login).
Future<bool> shouldShowOnboarding(HiveStorage hive) async {
  final done = hive.box(HiveBoxNames.appPrefs).get(pilotOnboardingDoneKey);
  return done != true;
}
