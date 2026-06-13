import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/farmer/data/geography_remote.dart';
import 'package:agriflow_mobile/features/farmer/domain/geo_option.dart';
import 'package:agriflow_mobile/features/farmer/presentation/farmer_list_screen.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final geographyRemoteProvider = Provider<GeographyRemote>((ref) {
  return GeographyRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

class FarmerCreateScreen extends ConsumerStatefulWidget {
  const FarmerCreateScreen({super.key});

  @override
  ConsumerState<FarmerCreateScreen> createState() => _FarmerCreateScreenState();
}

class _FarmerCreateScreenState extends ConsumerState<FarmerCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _mobileController = TextEditingController();

  List<GeoOption> _states = const [];
  List<GeoOption> _districts = const [];
  List<GeoOption> _blocks = const [];
  List<GeoOption> _clusters = const [];
  List<GeoOption> _officers = const [];

  GeoOption? _selectedState;
  GeoOption? _selectedDistrict;
  GeoOption? _selectedBlock;
  GeoOption? _selectedVillage;
  GeoOption? _selectedCluster;
  GeoOption? _selectedOfficer;

  bool _loadingStates = true;
  bool _loadingDistricts = false;
  bool _loadingBlocks = false;
  bool _loadingOptional = false;
  bool _saving = false;
  String? _geoError;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadStates());
  }

  @override
  void dispose() {
    _nameController.dispose();
    _mobileController.dispose();
    super.dispose();
  }

  Future<void> _loadStates() async {
    setState(() {
      _loadingStates = true;
      _geoError = null;
    });
    try {
      final states = await ref.read(geographyRemoteProvider).getStates();
      GeoOption? defaultState;
      for (final state in states) {
        if (state.name == 'Tamil Nadu' || state.label == 'Tamil Nadu') {
          defaultState = state;
          break;
        }
      }
      defaultState ??= states.isNotEmpty ? states.first : null;
      if (!mounted) return;
      setState(() {
        _states = states;
        _selectedState = defaultState;
        _loadingStates = false;
      });
      if (defaultState != null) {
        await _loadDistricts(defaultState.name);
      }
      await _loadOptionalLists();
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loadingStates = false;
        _geoError = AppLocalizations.of(context)!.errorGeneric;
      });
    }
  }

  Future<void> _loadDistricts(String stateName) async {
    setState(() {
      _loadingDistricts = true;
      _districts = const [];
      _blocks = const [];
      _selectedDistrict = null;
      _selectedBlock = null;
      _selectedVillage = null;
    });
    try {
      final districts =
          await ref.read(geographyRemoteProvider).getDistricts(stateName);
      if (!mounted) return;
      setState(() {
        _districts = districts;
        _loadingDistricts = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loadingDistricts = false);
    }
  }

  Future<void> _loadBlocks(String districtName) async {
    setState(() {
      _loadingBlocks = true;
      _blocks = const [];
      _selectedBlock = null;
      _selectedVillage = null;
    });
    try {
      final blocks =
          await ref.read(geographyRemoteProvider).getBlocks(districtName);
      if (!mounted) return;
      setState(() {
        _blocks = blocks;
        _loadingBlocks = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loadingBlocks = false);
    }
  }

  Future<void> _loadOptionalLists({String? block}) async {
    setState(() => _loadingOptional = true);
    try {
      final geo = ref.read(geographyRemoteProvider);
      final blockCode = _selectedBlock?.name ?? block;
      final clusters =
          await geo.getClusters(block: blockCode);
      final officers = await geo.getOfficers();
      if (!mounted) return;
      setState(() {
        _clusters = clusters;
        _officers = officers;
        _loadingOptional = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loadingOptional = false);
    }
  }

  Future<List<GeoOption>> _searchVillages(String query) async {
    final block = _selectedBlock;
    if (block == null || query.trim().length < 2) return const [];
    return ref.read(geographyRemoteProvider).searchVillages(
          block: block.name,
          search: query,
        );
  }

  Future<void> _save() async {
    final l10n = AppLocalizations.of(context)!;
    if (!_formKey.currentState!.validate()) return;
    if (_selectedState == null ||
        _selectedDistrict == null ||
        _selectedBlock == null ||
        _selectedVillage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.farmerGeographyRequired)),
      );
      return;
    }
    setState(() => _saving = true);
    try {
      await ref.read(farmerRemoteProvider).create({
        'farmer_name': _nameController.text.trim(),
        'mobile': _mobileController.text.trim(),
        'state': _selectedState!.name,
        'district': _selectedDistrict!.name,
        'block': _selectedBlock!.name,
        'village': _selectedVillage!.name,
        if (_selectedCluster != null) 'cluster': _selectedCluster!.name,
        if (_selectedOfficer != null) 'officer': _selectedOfficer!.name,
      });
      ref.invalidate(farmerListProvider);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.farmerCreateSuccess)),
      );
      context.pop();
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.errorGeneric)),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(title: Text(l10n.farmerCreateTitle)),
      body: _loadingStates
          ? const Center(child: CircularProgressIndicator())
          : Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (_geoError != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(_geoError!, style: const TextStyle(color: Colors.red)),
                    ),
                  TextFormField(
                    controller: _nameController,
                    decoration: InputDecoration(labelText: l10n.farmerNameLabel),
                    validator: (v) =>
                        (v == null || v.trim().isEmpty) ? l10n.farmerNameRequired : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _mobileController,
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(labelText: l10n.farmerMobileLabel),
                    validator: (v) {
                      final digits = (v ?? '').replaceAll(RegExp(r'\D'), '');
                      if (digits.length != 10) return l10n.farmerMobileRequired;
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  _geoDropdown(
                    label: l10n.geoStateLabel,
                    value: _selectedState,
                    items: _states,
                    loading: _loadingStates,
                    onChanged: (value) async {
                      setState(() => _selectedState = value);
                      if (value != null) await _loadDistricts(value.name);
                    },
                  ),
                  if (_districts.isNotEmpty || _loadingDistricts)
                    _geoDropdown(
                      label: l10n.geoDistrictLabel,
                      value: _selectedDistrict,
                      items: _districts,
                      loading: _loadingDistricts,
                    onChanged: (value) async {
                      setState(() {
                        _selectedDistrict = value;
                        _selectedBlock = null;
                        _selectedVillage = null;
                        _blocks = const [];
                      });
                      if (value != null) await _loadBlocks(value.name);
                    },
                    ),
                  if (_blocks.isNotEmpty || _loadingBlocks)
                    _geoDropdown(
                      label: l10n.geoBlockLabel,
                      value: _selectedBlock,
                      items: _blocks,
                      loading: _loadingBlocks,
                      onChanged: (value) async {
                        setState(() {
                          _selectedBlock = value;
                          _selectedVillage = null;
                        });
                        if (value != null) await _loadOptionalLists(block: value.name);
                      },
                    ),
                  if (_selectedBlock != null) ...[
                    const SizedBox(height: 8),
                    Autocomplete<GeoOption>(
                      displayStringForOption: (o) => o.label,
                      optionsBuilder: (query) => _searchVillages(query.text),
                      onSelected: (option) {
                        setState(() => _selectedVillage = option);
                      },
                      fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
                        if (_selectedVillage != null &&
                            controller.text.isEmpty) {
                          controller.text = _selectedVillage!.label;
                        }
                        return TextFormField(
                          controller: controller,
                          focusNode: focusNode,
                          decoration: InputDecoration(
                            labelText: l10n.geoVillageLabel,
                            helperText: l10n.geoVillageSearchHint,
                          ),
                          onChanged: (_) => setState(() => _selectedVillage = null),
                          validator: (_) =>
                              _selectedVillage == null ? l10n.geoVillageRequired : null,
                        );
                      },
                    ),
                  ],
                  const Divider(height: 32),
                  Text(
                    l10n.geoOptionalSection,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                  const SizedBox(height: 8),
                  _geoDropdown(
                    label: l10n.geoClusterLabel,
                    value: _selectedCluster,
                    items: _clusters,
                    loading: _loadingOptional,
                    optional: true,
                    onChanged: (value) => setState(() => _selectedCluster = value),
                  ),
                  _geoDropdown(
                    label: l10n.geoOfficerLabel,
                    value: _selectedOfficer,
                    items: _officers,
                    loading: _loadingOptional,
                    optional: true,
                    onChanged: (value) => setState(() => _selectedOfficer = value),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _saving ? null : _save,
                    child: _saving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(l10n.farmerSaveLabel),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _geoDropdown({
    required String label,
    required GeoOption? value,
    required List<GeoOption> items,
    required ValueChanged<GeoOption?> onChanged,
    bool loading = false,
    bool optional = false,
  }) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: optional ? label : '$label *',
          helperText: optional ? l10n.geoOptionalHelper : null,
        ),
        child: loading
            ? const LinearProgressIndicator()
            : DropdownButtonHideUnderline(
                child: DropdownButton<GeoOption>(
                  isExpanded: true,
                  value: value != null && items.any((i) => i.name == value.name)
                      ? value
                      : null,
                  hint: Text(label),
                  items: items
                      .map(
                        (item) => DropdownMenuItem(
                          value: item,
                          child: Text(item.label),
                        ),
                      )
                      .toList(),
                  onChanged: onChanged,
                ),
              ),
      ),
    );
  }
}
