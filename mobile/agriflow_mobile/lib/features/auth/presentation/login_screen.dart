import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _userController = TextEditingController();
  final _passController = TextEditingController();

  @override
  void dispose() {
    _userController.dispose();
    _passController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final auth = ref.watch(authSessionProvider);

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(l10n.appTitle, style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 8),
              Text(l10n.loginTitle),
              const SizedBox(height: 24),
              TextField(
                controller: _userController,
                decoration: InputDecoration(labelText: l10n.loginUsername),
                autocorrect: false,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _passController,
                decoration: InputDecoration(labelText: l10n.loginPassword),
                obscureText: true,
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: auth.isLoading
                    ? null
                    : () => ref.read(authSessionProvider.notifier).login(
                          _userController.text.trim(),
                          _passController.text,
                        ),
                child: Text(l10n.loginSubmit),
              ),
              if (Env.devAuthStubEnabled && !Env.demoMode) ...[
                const SizedBox(height: 12),
                OutlinedButton(
                  onPressed: auth.isLoading
                      ? null
                      : () => ref.read(authSessionProvider.notifier).loginDevStub(),
                  child: Text(l10n.loginDevStub),
                ),
              ],
              if (auth.hasError) ...[
                const SizedBox(height: 16),
                Text(
                  auth.error.toString(),
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
