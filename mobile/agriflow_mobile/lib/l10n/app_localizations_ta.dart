// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Tamil (`ta`).
class AppLocalizationsTa extends AppLocalizations {
  AppLocalizationsTa([String locale = 'ta']) : super(locale);

  @override
  String get appTitle => 'AgriFlow OS';

  @override
  String get loginTitle => 'உள்நுழைவு';

  @override
  String get loginUsername => 'பயனர் பெயர்';

  @override
  String get loginPassword => 'கடவுச்சொல்';

  @override
  String get loginSubmit => 'தொடரவும்';

  @override
  String get loginDevStub => 'சோதனை அமர்வு (debug)';

  @override
  String get navTimeline => 'காலவரிசை';

  @override
  String get navTasks => 'என் பணிகள்';

  @override
  String get navNotifications => 'அறிவிப்புகள்';

  @override
  String get navSync => 'ஒத்திசைவு';

  @override
  String get syncStatusTitle => 'ஒத்திசைவு நிலை';

  @override
  String get syncNow => 'இப்போது ஒத்திசை';

  @override
  String syncPending(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count நிலுவை',
      one: '1 நிலுவை',
      zero: 'நிலுவை இல்லை',
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
      'இணையம் இல்லை — இணைப்பு வந்ததும் ஒத்திசைக்கப்படும்';

  @override
  String get degradedNetworkBanner => 'மெதுவான இணையம் — ஒத்திசைவு தாமதமாகலாம்';

  @override
  String offlinePendingHint(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count மாற்றங்கள் காத்திருக்கின்றன',
      one: '1 மாற்றம் காத்திருக்கிறது',
    );
    return '$_temp0';
  }

  @override
  String syncPhaseLabel(String phase) {
    return 'ஒத்திசைவு: $phase';
  }

  @override
  String queueRepairResult(int reset, int deduped) {
    return 'சரிசெய்தல்: $reset மீட்டமை, $deduped நீக்கம்';
  }

  @override
  String get conflictStepsTitle => 'செய்ய வேண்டியவை';

  @override
  String get conflictStepRefresh =>
      'புதுப்பி என்பதைத் தட்டி சேவையக தரவைப் பெறுங்கள்';

  @override
  String get conflictStepReview => 'உங்கள் மாற்றத்தை மறுபார்வை செய்யுங்கள்';

  @override
  String get conflictStepRetry => 'தேவைப்பட்டால் மீண்டும் முயற்சிக்கவும்';

  @override
  String get emptyTasks => 'பணிகள் இல்லை';

  @override
  String get emptyTimeline => 'காலவரிசை நிகழ்வுகள் இல்லை';

  @override
  String get emptyNotifications => 'அறிவிப்புகள் இல்லை';

  @override
  String get errorGeneric => 'பிழை ஏற்பட்டது';

  @override
  String get retry => 'மீண்டும்';

  @override
  String get taskComplete => 'முடிந்தது';

  @override
  String get conflictTitle => 'ஒத்திசைவு முரண்பாடு';

  @override
  String get conflictExplanation =>
      'சேவையகத்தில் புதிய பதிப்பு உள்ளது. புதுப்பித்த பிறகு மீண்டும் முயற்சிக்கவும்.';

  @override
  String get conflictRefresh => 'சேவையகத்திலிருந்து புதுப்பி';

  @override
  String deviceHealthLabel(String score) {
    return 'சாதன நிலை: $score';
  }

  @override
  String get deviceStaleWarning =>
      'சமீபத்தில் ஒத்திசைவு இல்லை — Wi‑Fi இல் திறக்கவும்';

  @override
  String get notificationMarkRead => 'படித்தது';

  @override
  String get logout => 'வெளியேறு';

  @override
  String get feedbackTitle => 'சோதனை கருத்து';

  @override
  String get feedbackHint => 'களத்தில் நடந்ததை விவரிக்கவும்.';

  @override
  String get feedbackCategory => 'வகை';

  @override
  String get feedbackSeverity => 'முக்கியத்துவம்';

  @override
  String get feedbackBodyLabel => 'விவரங்கள்';

  @override
  String get feedbackBodyRequired => 'விவரங்களை உள்ளிடவும்';

  @override
  String get feedbackSubmit => 'அனுப்பு';

  @override
  String get feedbackSent => 'கருத்து அனுப்பப்பட்டது';

  @override
  String get feedbackCatSync => 'ஒத்திசைவு';

  @override
  String get feedbackCatUx => 'பயன்பாடு';

  @override
  String get feedbackCatInventory => 'சரக்கு';

  @override
  String get feedbackCatTask => 'பணிகள்';

  @override
  String get feedbackCatNetwork => 'பிணையம்';

  @override
  String get feedbackCatOther => 'மற்றவை';

  @override
  String get feedbackSevLow => 'குறைவு';

  @override
  String get feedbackSevMedium => 'நடுத்தர';

  @override
  String get feedbackSevHigh => 'உயர்';

  @override
  String get onboardingTitle => 'கள பயிற்சி';

  @override
  String get onboardingIntro =>
      'முதல் சோதனை நாளுக்கு முன் இந்த படிகளை முடிக்கவும்.';

  @override
  String get onboardingLogin => 'உள்நுழைவு';

  @override
  String get onboardingInitialSync => 'Wi‑Fi இல் முழு ஒத்திசைவு';

  @override
  String get onboardingReviewTasks => 'என் பணிகளை பார்வையிடு';

  @override
  String get onboardingOfflineTest => 'விருப்பம்: தரவு அணைத்து சோதனை';

  @override
  String get onboardingFeedback => 'கருத்து அனுப்பும் வழி அறிந்திரு';

  @override
  String get onboardingRequired => 'பரிந்துரை';

  @override
  String get onboardingDone => 'தொடரவும்';

  @override
  String appVersionLabel(String version) {
    return 'பதிப்பு $version';
  }

  @override
  String get navHome => 'முகப்பு';

  @override
  String get navFarmers => 'விவசாயிகள்';

  @override
  String dashboardWelcome(String name) {
    return 'வணக்கம், $name';
  }

  @override
  String dashboardRoleLine(String role) {
    return 'பங்கு: $role';
  }

  @override
  String dashboardBlocksLine(String blocks) {
    return 'பிரிவுகள்: $blocks';
  }

  @override
  String get dashboardProjects => 'திட்டங்கள்';

  @override
  String get dashboardOpenTasks => 'திறந்த பணிகள்';

  @override
  String get dashboardViewFarmers => 'விவசாயிகளைப் பார்';

  @override
  String get roleOwner => 'உரிமையாளர்';

  @override
  String get roleOfficeManager => 'அலுவலக மேலாளர்';

  @override
  String get roleFieldStaff => 'களப் பணியாளர்';

  @override
  String get roleUser => 'பயனர்';

  @override
  String get emptyFarmers => 'விவசாயிகள் இல்லை';

  @override
  String get noProjectForFarmer => 'இந்த விவசாயிக்கு செயலில் திட்டம் இல்லை';

  @override
  String get projectTimelineTitle => 'திட்ட காலவரிசை';

  @override
  String advanceStage(String stage) {
    return '$stage க்கு முன்னேறு';
  }

  @override
  String get stageTransitionSuccess =>
      'நிலை புதுப்பிக்கப்பட்டது — பணிகளுக்கு ஒத்திசைவு செய்யுங்கள்';

  @override
  String get timelineNoteLabel => 'குறிப்பு';

  @override
  String get timelineNoteQueue => 'குறிப்பை வரிசையில் சேர்';

  @override
  String get syncLastRequestId => 'கடைசி கோரிக்கை ID';

  @override
  String get syncRepairQueue => 'வரிசையை சரிசெய்';

  @override
  String get taskMaterialsTitle => 'பொருட்கள்';

  @override
  String get taskConsumeOne => '1 நுகர்வு';

  @override
  String get notificationTaskDue => 'பணி காலக்கெடு';

  @override
  String get notificationTaskOverdue => 'பணி தாமதம்';

  @override
  String get notificationStageTransition => 'நிலை மாற்றம்';

  @override
  String get notificationProjectStatus => 'திட்ட புதுப்பிப்பு';

  @override
  String get notificationSlaBreach => 'SLA மீறல்';

  @override
  String get notificationManual => 'அறிவிப்பு';

  @override
  String get stageLeadCaptured => 'லீட் பதிவு';

  @override
  String get stageEligibilityCheck => 'தகுதி சரிபார்ப்பு';

  @override
  String get stageDocumentsCollected => 'ஆவணங்கள் சேகரம்';

  @override
  String get stageMimisRegistered => 'MIMIS பதிவு';

  @override
  String get stageFieldSurvey => 'களஆய்வு';

  @override
  String get stageQuotationGenerated => 'மதிப்பீடு';

  @override
  String get stagePreInspectionApproval => 'முன் ஆய்வு ஒப்புதல்';

  @override
  String get stageWorkOrderReceived => 'பணி ஆணை';

  @override
  String get stageMaterialDispatched => 'பொருள் அனுப்பப்பட்டது';

  @override
  String get stageInstallationDone => 'நிறுவல் முடிந்தது';

  @override
  String get stagePostInspectionApproval => 'பின் ஆய்வு ஒப்புதல்';

  @override
  String get stageSubsidyReleased => 'உதவித்தொகை வழங்கப்பட்டது';

  @override
  String get timelineStageToday => 'இன்று';

  @override
  String get timelineStagePending => 'நிலுவை';

  @override
  String get timelineStageLocked => 'பூட்டப்பட்டது';

  @override
  String timelineStageBy(String name) {
    return '$name மூலம்';
  }

  @override
  String get timelineActionCall => 'அழை';

  @override
  String get timelineActionWhatsapp => 'வாட்ஸ்அப்';

  @override
  String get timelineActionNote => 'குறிப்பு';

  @override
  String timelineBlockerMissing(String item) {
    return 'காணவில்லை: $item';
  }

  @override
  String timelineHeaderLocation(String block, String village, String acres) {
    return '$block · $village$acres';
  }

  @override
  String get timelineHeaderSchemeDrip => 'டிரிப் பாசனம் · உதவித்தொகை திட்டம்';

  @override
  String get timelineHeaderSchemeSubsidy => 'உதவித்தொகை டிரிப் திட்டம்';

  @override
  String timelineHeaderProject(String id) {
    return 'திட்டம் $id';
  }

  @override
  String timelineHeaderOfficer(String name) {
    return 'அலுவலர்: $name';
  }

  @override
  String timelineHeaderReferral(String name) {
    return 'பரிந்துரை: $name';
  }

  @override
  String get timelineAcres => 'ஏக்கர்';

  @override
  String get taskFeedTitle => 'இன்றைய பணிகள்';

  @override
  String taskFeedSummary(int pending, int overdue) {
    return '$pending நிலுவை · $overdue தாமதம்';
  }

  @override
  String get taskSectionOverdue => 'தாமதம்';

  @override
  String get taskSectionToday => 'இன்று';

  @override
  String get taskSectionUpcoming => 'வரவிருக்கும்';

  @override
  String get taskFeedEmptyCelebration => '🎉 இன்று நிலுவை பணிகள் இல்லை!';

  @override
  String get taskFilterAll => 'அனைத்தும்';

  @override
  String get taskFilterMine => 'என் பணிகள்';

  @override
  String get taskFilterVisit => 'வருகை';

  @override
  String get taskFilterDocument => 'ஆவணம்';

  @override
  String get taskDueToday => 'இன்று காலக்கெடு';

  @override
  String taskDueDaysAgo(int days) {
    return '$days நாள் முன்பு';
  }

  @override
  String taskDueInDays(int days) {
    return '$days நாளில்';
  }

  @override
  String get taskGpsCheckIn => 'கள GPS பதிவு';

  @override
  String get taskGpsCheckedIn => 'களத்தில் பதிவு செய்யப்பட்டது';

  @override
  String get taskVoiceNoteAttach => 'குரல் குறிப்பு இணை';

  @override
  String get taskVoiceNoteQueued => 'குரல் குறிப்பு ஒத்திசைவுக்கு வரிசையில்';

  @override
  String get notificationMarkAllRead => 'அனைத்தையும் படித்தது';

  @override
  String get notificationEmptyFriendly =>
      'புதிய அறிவிப்புகள் இல்லை — நீங்கள் புதுப்பித்த நிலையில்.';

  @override
  String get notificationFilterAll => 'அனைத்தும்';

  @override
  String get notificationFilterUrgent => 'அவசரம்';

  @override
  String get notificationFilterTasks => 'பணிகள்';

  @override
  String get notificationGroupToday => 'இன்று';

  @override
  String get notificationGroupYesterday => 'நேற்று';

  @override
  String get notificationGroupThisWeek => 'இந்த வாரம்';

  @override
  String get notificationGroupOlder => 'பழையவை';

  @override
  String get notificationFollowupMissed => 'பின்தொடர்தல் தவறு';

  @override
  String get notificationStageStuck => 'நிலை சிக்கல்';

  @override
  String get notificationOfficerTransfer => 'அலுவலர் மாற்றம்';

  @override
  String get notificationLowStock => 'குறைந்த சரக்கு';

  @override
  String get notificationTaskCompleted => 'பணி முடிந்தது';

  @override
  String syncBarOnline(int count) {
    return 'ஆன்லைன் · $count நிலுவை';
  }

  @override
  String syncBarOffline(int count) {
    return 'ஆஃப்லைன் · $count நிலுவை';
  }

  @override
  String syncBarSyncing(int current, int total) {
    return 'ஒத்திசைவு $current / $total…';
  }

  @override
  String get syncBarJustSynced => 'இப்போது ஒத்திசைக்கப்பட்டது';

  @override
  String get syncBarTapHintOnline => 'ஒத்திசைவு தாவலில் கட்டாய புதுப்பிப்பு';

  @override
  String get syncBarTapHintOffline =>
      'மாற்றங்கள் சேமிக்கப்பட்டன — ஆன்லைனில் ஒத்திசைக்கவும்';

  @override
  String get syncToastSavedOffline => 'ஆஃப்லைனில் சேமிக்கப்பட்டது ✓';

  @override
  String get syncToastComplete => 'ஒத்திசைவு முடிந்தது ✓';

  @override
  String get syncToastStarted => 'மாற்றங்கள் ஒத்திசைக்கப்படுகின்றன…';

  @override
  String get syncForceNow => 'இப்போது கட்டாய ஒத்திசைவு';

  @override
  String syncLastSuccessLabel(String time) {
    return 'கடைசி வெற்றி ஒத்திசைவு: $time';
  }

  @override
  String syncPendingChanges(int count) {
    return 'நிலுவை மாற்றங்கள்: $count';
  }

  @override
  String get syncPendingListTitle => 'நிலுவை வரிசை';

  @override
  String get syncPendingListEmpty => 'வரிசையில் மாற்றங்கள் இல்லை';

  @override
  String get syncHistoryTitle => 'ஒத்திசைவு வரலாறு (கடைசி 10)';

  @override
  String get syncHistoryEmpty => 'ஒத்திசைவு பதிவு இல்லை';

  @override
  String get syncHistoryOk => 'சரி';

  @override
  String get syncHistoryFail => 'தோல்வி';

  @override
  String get syncDeveloperTitle => 'டெவலப்பர் (டெமோ)';

  @override
  String get syncSimulateOffline => 'ஆஃப்லைன் சோதனை';

  @override
  String get syncSimulateOfflineHint =>
      'நெட்வொர்க் இல்லாமல் வரிசை — நேரடி டெமோவுக்கு';

  @override
  String get syncSimulateOfflineOn => 'ஆஃப்லைன் சோதனை இயக்கம்';

  @override
  String get syncSimulateOfflineOff => 'ஆஃப்லைன் சோதனை அணைப்பு';

  @override
  String get syncDemoFlowButton => 'டெமோ: ஆன்லைன் + ஒத்திசைவு';

  @override
  String get syncNever => 'இதுவரை இல்லை';

  @override
  String get syncJustNow => 'இப்போதே';

  @override
  String syncMinutesAgo(int minutes) {
    return '$minutes நிமி முன்பு';
  }

  @override
  String syncHoursAgo(int hours) {
    return '$hours மணி முன்பு';
  }

  @override
  String sectionWithCount(String label, int count) {
    return '$label ($count)';
  }

  @override
  String syncFlyingItem(int index) {
    return 'பதிவேற்றம் $index';
  }

  @override
  String conflictStepNumbered(int step, String text) {
    return '$step. $text';
  }

  @override
  String conflictMutationId(String id) {
    return 'மாற்றம்: $id';
  }

  @override
  String conflictVersionLine(int server, int client) {
    return 'சேவையகம் v$server · கிளையன்ட் v$client';
  }

  @override
  String get conflictCodeDefault => 'ஒத்திசைவு முரண்பாடு';

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
    return 'ஒதுக்கப்பட்டது $qty · $status';
  }

  @override
  String updateRequiredMessage(String version) {
    return 'புதுப்பிப்பு தேவை (குறைந்தபட்சம் $version)';
  }

  @override
  String get stageSecondaryDocsComplete => '4/4 ஆவணங்கள் பதிவேற்றம்';

  @override
  String stageSecondaryMimisId(String id) {
    return 'ID: $id';
  }

  @override
  String stageSecondaryQuotation(String amount) {
    return '₹$amount';
  }

  @override
  String get stageSecondaryAaoApproved => 'AAO ஒப்புதல்';

  @override
  String get stageSecondaryStockReserved => 'சரக்கு ஒதுக்கப்பட்டது';

  @override
  String get stageSecondaryInstallationTeam => 'முருகன் நிறுவல் குழு';
}
