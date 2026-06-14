// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'AgriFlow OS';

  @override
  String get loginTitle => 'Sign in';

  @override
  String get loginUsername => 'Username';

  @override
  String get loginPassword => 'Password';

  @override
  String get loginSubmit => 'Continue';

  @override
  String get loginDevStub => 'Use dev session (debug only)';

  @override
  String get navTimeline => 'Timeline';

  @override
  String get navTasks => 'My Tasks';

  @override
  String get navNotifications => 'Notifications';

  @override
  String get navSync => 'Sync';

  @override
  String get syncStatusTitle => 'Sync status';

  @override
  String get syncNow => 'Sync now';

  @override
  String syncPending(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count pending changes',
      one: '1 pending change',
      zero: 'No pending changes',
    );
    return '$_temp0';
  }

  @override
  String get syncInProgress => 'Syncing…';

  @override
  String syncLastSuccess(String time) {
    return 'Last sync: $time';
  }

  @override
  String get offlineBanner =>
      'You are offline — changes will sync when connected';

  @override
  String get degradedNetworkBanner =>
      'Slow or limited connection — sync may take longer';

  @override
  String offlinePendingHint(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count changes waiting to sync',
      one: '1 change waiting to sync',
    );
    return '$_temp0';
  }

  @override
  String syncPhaseLabel(String phase) {
    return 'Sync step: $phase';
  }

  @override
  String queueRepairResult(int reset, int deduped) {
    return 'Queue repair: $reset reset, $deduped duplicates removed';
  }

  @override
  String get conflictStepsTitle => 'What to do';

  @override
  String get conflictStepRefresh =>
      'Tap Refresh to pull the latest server data';

  @override
  String get conflictStepReview => 'Review your task or inventory change';

  @override
  String get conflictStepRetry => 'Make the change again if still needed';

  @override
  String get emptyTasks => 'No tasks in your inbox';

  @override
  String get emptyTimeline => 'No timeline events yet';

  @override
  String get emptyNotifications => 'No notifications';

  @override
  String get errorGeneric => 'Something went wrong';

  @override
  String get retry => 'Retry';

  @override
  String get taskComplete => 'Mark complete';

  @override
  String get conflictTitle => 'Sync conflict';

  @override
  String get conflictExplanation =>
      'The server has a newer version of this record. Your offline change cannot apply until you refresh and try again.';

  @override
  String get conflictRefresh => 'Refresh from server';

  @override
  String deviceHealthLabel(String score) {
    return 'Device health: $score';
  }

  @override
  String get deviceStaleWarning =>
      'Device not synced recently — open app on Wi‑Fi';

  @override
  String get notificationMarkRead => 'Mark read';

  @override
  String get logout => 'Sign out';

  @override
  String get feedbackTitle => 'Pilot feedback';

  @override
  String get feedbackHint =>
      'Describe what happened in the field. No farmer PII in free text.';

  @override
  String get feedbackCategory => 'Category';

  @override
  String get feedbackSeverity => 'Severity';

  @override
  String get feedbackBodyLabel => 'Details';

  @override
  String get feedbackBodyRequired => 'Please enter feedback details';

  @override
  String get feedbackSubmit => 'Send feedback';

  @override
  String get feedbackSent => 'Feedback sent — thank you';

  @override
  String get feedbackCatSync => 'Sync';

  @override
  String get feedbackCatUx => 'App UX';

  @override
  String get feedbackCatInventory => 'Inventory';

  @override
  String get feedbackCatTask => 'Tasks';

  @override
  String get feedbackCatNetwork => 'Network';

  @override
  String get feedbackCatOther => 'Other';

  @override
  String get feedbackSevLow => 'Low';

  @override
  String get feedbackSevMedium => 'Medium';

  @override
  String get feedbackSevHigh => 'High';

  @override
  String get onboardingTitle => 'Field onboarding';

  @override
  String get onboardingIntro =>
      'Complete these steps before your first pilot day.';

  @override
  String get onboardingLogin => 'Sign in with your officer account';

  @override
  String get onboardingInitialSync => 'Run a full sync on Wi‑Fi';

  @override
  String get onboardingReviewTasks => 'Open My Tasks and review assignments';

  @override
  String get onboardingOfflineTest =>
      'Optional: turn off data and confirm cached views';

  @override
  String get onboardingFeedback =>
      'Know how to send pilot feedback from the menu';

  @override
  String get onboardingRequired => 'Recommended';

  @override
  String get onboardingDone => 'Continue to app';

  @override
  String appVersionLabel(String version) {
    return 'App version $version';
  }

  @override
  String get navHome => 'Home';

  @override
  String get navFarmers => 'Farmers';

  @override
  String dashboardWelcome(String name) {
    return 'Welcome, $name';
  }

  @override
  String dashboardRoleLine(String role) {
    return 'Role: $role';
  }

  @override
  String dashboardBlocksLine(String blocks) {
    return 'Blocks: $blocks';
  }

  @override
  String get dashboardProjects => 'Projects';

  @override
  String get dashboardOpenTasks => 'Open tasks';

  @override
  String get dashboardViewFarmers => 'View farmers';

  @override
  String get roleOwner => 'Owner';

  @override
  String get roleOfficeManager => 'Office Manager';

  @override
  String get roleFieldStaff => 'Field Staff';

  @override
  String get roleUser => 'User';

  @override
  String get emptyFarmers => 'No farmers found';

  @override
  String get noProjectForFarmer => 'No active project for this farmer';

  @override
  String get projectTimelineTitle => 'Project timeline';

  @override
  String advanceStage(String stage) {
    return 'Advance to $stage';
  }

  @override
  String get stageTransitionSuccess => 'Stage updated — sync to refresh tasks';

  @override
  String get timelineNoteLabel => 'Note';

  @override
  String get timelineNoteQueue => 'Queue note';

  @override
  String get syncLastRequestId => 'Last request ID';

  @override
  String get syncRepairQueue => 'Repair queue';

  @override
  String get taskMaterialsTitle => 'Materials';

  @override
  String get taskConsumeOne => 'Consume 1';

  @override
  String get notificationTaskDue => 'Task due';

  @override
  String get notificationTaskOverdue => 'Task overdue';

  @override
  String get notificationStageTransition => 'Stage updated';

  @override
  String get notificationProjectStatus => 'Project update';

  @override
  String get notificationSlaBreach => 'SLA breach';

  @override
  String get notificationManual => 'Notification';

  @override
  String get stageLeadCaptured => 'Lead captured';

  @override
  String get stageEligibilityCheck => 'Eligibility check';

  @override
  String get stageDocumentsCollected => 'Documents collected';

  @override
  String get stageMimisRegistered => 'MIMIS registered';

  @override
  String get stageFieldSurvey => 'Field survey';

  @override
  String get stageQuotationGenerated => 'Quotation generated';

  @override
  String get stagePreInspectionApproval => 'Pre-inspection approval';

  @override
  String get stageWorkOrderReceived => 'Work order received';

  @override
  String get stageMaterialDispatched => 'Material dispatched';

  @override
  String get stageInstallationDone => 'Installation done';

  @override
  String get stagePostInspectionApproval => 'Post-inspection approval';

  @override
  String get stageSubsidyReleased => 'Subsidy released';

  @override
  String get timelineStageToday => 'TODAY';

  @override
  String get timelineStagePending => 'Pending';

  @override
  String get timelineStageLocked => 'Locked';

  @override
  String timelineStageBy(String name) {
    return 'By $name';
  }

  @override
  String get timelineActionCall => 'Call';

  @override
  String get timelineActionWhatsapp => 'WhatsApp';

  @override
  String get timelineActionNote => 'Note';

  @override
  String timelineBlockerMissing(String item) {
    return 'Missing: $item';
  }

  @override
  String timelineHeaderLocation(String block, String village, String acres) {
    return '$block · $village$acres';
  }

  @override
  String get timelineHeaderSchemeDrip => 'Drip irrigation · subsidy project';

  @override
  String get timelineHeaderSchemeSubsidy => 'Subsidy drip project';

  @override
  String timelineHeaderProject(String id) {
    return 'Project $id';
  }

  @override
  String timelineHeaderOfficer(String name) {
    return 'Officer: $name';
  }

  @override
  String timelineHeaderReferral(String name) {
    return 'Referred by: $name';
  }

  @override
  String get timelineAcres => 'acres';

  @override
  String get taskFeedTitle => 'Today\'s work';

  @override
  String taskFeedSummary(int pending, int overdue) {
    return '$pending pending · $overdue overdue';
  }

  @override
  String get taskSectionOverdue => 'Overdue';

  @override
  String get taskSectionToday => 'Today';

  @override
  String get taskSectionUpcoming => 'Upcoming';

  @override
  String get taskFeedEmptyCelebration => '🎉 No pending tasks today!';

  @override
  String get taskFilterAll => 'All';

  @override
  String get taskFilterMine => 'My tasks';

  @override
  String get taskFilterVisit => 'Visit';

  @override
  String get taskFilterDocument => 'Documents';

  @override
  String get taskDueToday => 'Due today';

  @override
  String taskDueDaysAgo(int days) {
    return '$days days ago';
  }

  @override
  String taskDueInDays(int days) {
    return 'In $days days';
  }

  @override
  String get taskGpsCheckIn => 'GPS check-in at field';

  @override
  String get taskGpsCheckedIn => 'Checked in at field';

  @override
  String get taskVoiceNoteAttach => 'Attach voice note';

  @override
  String get taskVoiceNoteQueued => 'Voice note queued for sync';

  @override
  String get notificationMarkAllRead => 'Mark all read';

  @override
  String get notificationEmptyFriendly =>
      'You\'re all caught up — no new alerts.';

  @override
  String get notificationFilterAll => 'All';

  @override
  String get notificationFilterUrgent => 'Urgent';

  @override
  String get notificationFilterTasks => 'Tasks';

  @override
  String get notificationGroupToday => 'Today';

  @override
  String get notificationGroupYesterday => 'Yesterday';

  @override
  String get notificationGroupThisWeek => 'This week';

  @override
  String get notificationGroupOlder => 'Older';

  @override
  String get notificationFollowupMissed => 'Missed follow-up';

  @override
  String get notificationStageStuck => 'Stage stuck';

  @override
  String get notificationOfficerTransfer => 'Officer transfer';

  @override
  String get notificationLowStock => 'Low stock alert';

  @override
  String get notificationTaskCompleted => 'Task completed';

  @override
  String syncBarOnline(int count) {
    return 'Online · $count pending';
  }

  @override
  String syncBarOffline(int count) {
    return 'Offline · $count pending';
  }

  @override
  String syncBarSyncing(int current, int total) {
    return 'Syncing $current of $total…';
  }

  @override
  String get syncBarJustSynced => 'All synced just now';

  @override
  String get syncBarTapHintOnline => 'Tap Sync tab to force refresh';

  @override
  String get syncBarTapHintOffline =>
      'Changes saved locally — sync when online';

  @override
  String get syncToastSavedOffline => 'Saved offline ✓';

  @override
  String get syncToastComplete => 'Synced ✓';

  @override
  String get syncToastStarted => 'Syncing your changes…';

  @override
  String get syncForceNow => 'Force sync now';

  @override
  String syncLastSuccessLabel(String time) {
    return 'Last successful sync: $time';
  }

  @override
  String syncPendingChanges(int count) {
    return 'Pending changes: $count items';
  }

  @override
  String get syncPendingListTitle => 'Pending queue';

  @override
  String get syncPendingListEmpty => 'No pending changes in queue';

  @override
  String get syncHistoryTitle => 'Sync history (last 10)';

  @override
  String get syncHistoryEmpty => 'No sync runs logged yet';

  @override
  String get syncHistoryOk => 'OK';

  @override
  String get syncHistoryFail => 'Failed';

  @override
  String get syncDeveloperTitle => 'Developer (demo)';

  @override
  String get syncSimulateOffline => 'Simulate offline';

  @override
  String get syncSimulateOfflineHint =>
      'Queue writes without network — for live demo';

  @override
  String get syncSimulateOfflineOn => 'Simulated offline ON';

  @override
  String get syncSimulateOfflineOff => 'Simulated offline OFF';

  @override
  String get syncDemoFlowButton => 'Demo: go online & sync';

  @override
  String get syncNever => 'Never';

  @override
  String get syncJustNow => 'Just now';

  @override
  String syncMinutesAgo(int minutes) {
    return '$minutes min ago';
  }

  @override
  String syncHoursAgo(int hours) {
    return '$hours hr ago';
  }

  @override
  String sectionWithCount(String label, int count) {
    return '$label ($count)';
  }

  @override
  String syncFlyingItem(int index) {
    return 'Upload $index';
  }

  @override
  String conflictStepNumbered(int step, String text) {
    return '$step. $text';
  }

  @override
  String conflictMutationId(String id) {
    return 'Mutation: $id';
  }

  @override
  String conflictVersionLine(int server, int client) {
    return 'Server v$server · Client v$client';
  }

  @override
  String get conflictCodeDefault => 'Sync conflict';

  @override
  String syncQueueItemTitle(String entity, String op) {
    return '$entity · $op';
  }

  @override
  String taskFarmerVillageLine(String farmer, String village) {
    return '$farmer · $village';
  }

  @override
  String taskStatusProjectLine(String status, String project) {
    return '$status · $project';
  }

  @override
  String taskReservedQty(String qty, String status) {
    return 'Reserved $qty · $status';
  }

  @override
  String updateRequiredMessage(String version) {
    return 'Update required (minimum $version)';
  }

  @override
  String get stageSecondaryDocsComplete => '4/4 documents uploaded';

  @override
  String stageSecondaryMimisId(String id) {
    return 'ID: $id';
  }

  @override
  String stageSecondaryQuotation(String amount) {
    return '₹$amount';
  }

  @override
  String get stageSecondaryAaoApproved => 'AAO approved';

  @override
  String get stageSecondaryStockReserved => 'Stock reserved';

  @override
  String get stageSecondaryInstallationTeam => 'Murugan installation team';

  @override
  String get farmerCreateTitle => 'New farmer';

  @override
  String get farmerNameLabel => 'Farmer name';

  @override
  String get farmerNameRequired => 'Enter farmer name';

  @override
  String get farmerMobileLabel => 'Mobile';

  @override
  String get farmerMobileRequired => 'Enter a valid 10-digit mobile number';

  @override
  String get farmerGeographyRequired =>
      'Select state, district, block, and village';

  @override
  String get farmerCreateSuccess => 'Farmer saved';

  @override
  String get farmerSaveLabel => 'Save';

  @override
  String get geoStateLabel => 'State';

  @override
  String get geoDistrictLabel => 'District';

  @override
  String get geoBlockLabel => 'Block';

  @override
  String get geoVillageLabel => 'Village';

  @override
  String get geoVillageSearchHint => 'Type at least 2 letters to search';

  @override
  String get geoVillageRequired => 'Select a village';

  @override
  String get geoClusterLabel => 'Cluster';

  @override
  String get geoOfficerLabel => 'Officer';

  @override
  String get geoOptionalSection => 'Optional';

  @override
  String get geoOptionalHelper => 'Optional — not required';

  @override
  String get actionVerifyEligibility => 'Verify eligibility';

  @override
  String get actionCollectDocuments => 'Collect documents';

  @override
  String get actionRegisterInMimis => 'Register in MIMIS';

  @override
  String get actionScheduleFieldSurvey => 'Schedule field survey';

  @override
  String get actionGenerateQuotation => 'Generate quotation';

  @override
  String get actionSubmitForPreInspection => 'Submit for pre-inspection';

  @override
  String get actionReceiveWorkOrder => 'Receive work order';

  @override
  String get actionDispatchMaterial => 'Dispatch material';

  @override
  String get actionCompleteInstallation => 'Complete installation';

  @override
  String get actionSubmitForPostInspection => 'Submit for post-inspection';

  @override
  String get actionReleaseSubsidy => 'Release subsidy';

  @override
  String get confirmStageTransition => 'Confirm stage transition';

  @override
  String get confirmMessageAdvance => 'Advance to the next stage?';

  @override
  String get transitionSuccess => 'Stage updated successfully';

  @override
  String get transitionFailed => 'Stage transition failed';

  @override
  String get currentStageLabel => 'Current stage';

  @override
  String stageXOf12(int current) {
    return '$current / 12';
  }

  @override
  String get workflowNoActionsForRole => 'No actions available for your role';

  @override
  String get cancel => 'Cancel';

  @override
  String get confirm => 'Confirm';

  @override
  String get billing => 'Billing';

  @override
  String get cashCarryTitle => 'Cash & Carry';

  @override
  String get cashAndCarryPos => 'Cash & Carry POS';

  @override
  String get itemSearchHint => 'Search items (e.g. Drip, Pipe, Motor)...';

  @override
  String get cartTotal => 'Total';

  @override
  String get cartEmpty => 'Cart is empty';

  @override
  String get cartEmptyHint => 'Search items above and tap to add';

  @override
  String get cartClear => 'Clear';

  @override
  String get saveInvoice => 'Save invoice';

  @override
  String get proceedToPayment => 'Proceed to payment';

  @override
  String get customerNameOptional => 'Customer name (optional)';

  @override
  String get customerMobileOptional => 'Mobile (optional)';

  @override
  String get paymentModeLabel => 'Payment mode';

  @override
  String get customerDetailsTitle => 'Customer details';

  @override
  String get invoiceCreatedTitle => 'Invoice created!';

  @override
  String get noItemsFound => 'No items found';

  @override
  String itemAddedToCart(String item) {
    return '$item added to cart';
  }

  @override
  String invoiceItemsCount(int count) {
    return '$count items';
  }

  @override
  String get paymentModeCash => 'Cash';

  @override
  String get paymentModeUpi => 'UPI';

  @override
  String get paymentModeCard => 'Card';

  @override
  String get paymentModeBankTransfer => 'Bank transfer';

  @override
  String get paymentModeMixed => 'Mixed';

  @override
  String get projectSale => 'Project Sale';

  @override
  String projectSaleTitle(String project) {
    return 'Project Sale: $project';
  }

  @override
  String get generateInvoice => 'Generate invoice';

  @override
  String get generateProjectInvoice => 'Generate project invoice';

  @override
  String get govtSubsidy => 'Govt subsidy (80%)';

  @override
  String get farmerPortion => 'Farmer portion (20%)';

  @override
  String get subsidySplit => 'Subsidy split';

  @override
  String get confirmGenerate => 'Confirm & generate';

  @override
  String get projectSaleSearchHint => 'Search items for quotation...';

  @override
  String get projectSaleEmptyHint => 'Add items to create quotation';

  @override
  String get projectSaleConfirmTitle => 'Confirm project invoice';

  @override
  String get projectSaleProjectLabel => 'Project';

  @override
  String get projectSaleFarmerLabel => 'Farmer';

  @override
  String get govtSubsidyAmount => 'Govt subsidy ₹';

  @override
  String get farmerPortionAmount => 'Farmer ₹';

  @override
  String projectSaleSplitError(double total) {
    final intl.NumberFormat totalNumberFormat =
        intl.NumberFormat.decimalPattern(localeName);
    final String totalString = totalNumberFormat.format(total);

    return 'Subsidy + farmer portion must equal total (₹$totalString)';
  }

  @override
  String get share_pdf => 'Share PDF';

  @override
  String get share_failed => 'Share failed';

  @override
  String get pdf_generated => 'PDF generated';

  @override
  String get service_visits => 'Service Visits';

  @override
  String get upcoming_visits => 'Upcoming Visits';

  @override
  String get visit_completed => 'Visit Completed';

  @override
  String get mark_complete => 'Mark Complete';

  @override
  String get farmer_satisfaction => 'Farmer Satisfaction';

  @override
  String get issues_found => 'Issues Found';

  @override
  String get actions_taken => 'Actions Taken';

  @override
  String get follow_up_required => 'Follow-up Required';

  @override
  String get service_checklist => 'Service Checklist';
}
