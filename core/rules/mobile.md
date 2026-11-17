# Mobile — behaviour only phones and tablets have

Loaded for mobile apps (native, cross-platform or a hybrid WebView shell). Shared UI rules are in [ux.md](ux.md) and [a11y.md](a11y.md); store requirements in [store.md](store.md); secure storage, transport and tokens in the safe phase (AUTH-02, SEC-04).

### MUX-14 [HIGH] Content under system bars, cutouts or the keyboard
- **Detect:** screens without safe-area or window-inset handling (content under the status bar, notch, Dynamic Island, home indicator or gesture bar); edge-to-edge drawing (enforced when an Android app targets API 35) with no inset padding; text fields hidden by the on-screen keyboard; fixed bottom bars over the keyboard; a hybrid WebView without `viewport-fit=cover` and `env(safe-area-inset-*)`.
- **Mech:** T `git grep -nIE 'SafeArea|safeAreaInset|ignoresSafeArea|WindowInsets|imePadding|enableEdgeToEdge|env\(safe-area-inset|viewport-fit|resizeToAvoidBottomInset|adjustResize|KeyboardAvoidingView' -- ':!*.md'`
- **Fix:** the platform's inset APIs on every screen root; scroll the focused field into view above the keyboard; test on a device with a cutout, a gesture bar and in landscape.
- **Impact:** buttons sit under the home indicator or keyboard and cannot be tapped.
- **Source:** Android, Display content edge-to-edge (https://developer.android.com/develop/ui/views/layout/edge-to-edge); Apple HIG, Layout (safe areas).

### MUX-21 [HIGH] Back navigation inconsistent
- **Detect:** the Android back button or gesture closing the app from an inner screen (common in hybrid shells), resetting the stack, or doing something different per screen; back interception with the deprecated `onBackPressed` that breaks predictive back; the iOS swipe-back gesture disabled without reason.
- **Mech:** T `git grep -nIE 'onBackPressed|OnBackPressedCallback|enableOnBackInvokedCallback|PopScope|WillPopScope|BackHandler|backButton|interactivePopGestureRecognizer' -- ':!*.md'`
- **Fix:** back pops one level, closes the top sheet or dialog first, and exits only from the root; use `OnBackPressedCallback`/`PopScope` so predictive back works; keep swipe-back; unsaved input follows UX-NS-01.
- **Impact:** users lose their place or quit the app by accident.
- **Source:** Least astonishment; Android, Add support for the predictive back gesture; Apple HIG, Navigation.

### MARC-06 [HIGH] State lost when the OS kills the app
- **Detect:** form input, navigation stack, selected tab or scroll position lost after the process is killed in the background, after rotation or after switching tabs; no use of the platform's state restoration.
- **Mech:** T `git grep -nIE 'onSaveInstanceState|rememberSaveable|SavedStateHandle|RestorationMixin|restorationId|restorationScopeId|@SceneStorage|NSUserActivity' -- ':!*.md'`
- **Fix:** save UI state through the platform mechanism (saved-state handles, restoration IDs, scene storage); keep scroll position per tab; test with "Don't keep activities" or by killing the process in the background.
- **Impact:** users who switch apps for a moment come back to an empty form or the start screen.
- **Source:** Android, Save UI states; Apple, Restoring your app's state.

### MUX-12 [HIGH] Permission requested out of context
- **Detect:** camera, location, contacts, photos, microphone or notification permission requested at launch or on a screen unrelated to the feature; no explanation before the system dialog; no handling of "denied" or "don't ask again" (a dead feature with no route to settings).
- **Mech:** T `git grep -nIE 'requestPermission|requestAuthorization|requestWhenInUseAuthorization|requestPermissions\(|ActivityCompat\.requestPermissions|Permission\.[a-zA-Z]+\.request|PermissionsAndroid\.request|registerForRemoteNotifications' -- ':!*.md'`
- **Fix:** ask when the user starts the feature that needs it, after a short in-app explanation; on denial, degrade the feature and offer a link to settings.
- **Impact:** users deny permissions they do not understand, and a denied system prompt usually cannot be shown again.
- **Source:** Least privilege; Apple HIG, Privacy (requesting permission); Android, Request runtime permissions.

### MPRF-07 [HIGH] Battery drained by background work
- **Detect:** continuous high-accuracy location when coarse or significant-change would do; wake locks without release or timeout; periodic timers or polling while backgrounded; background network work outside the platform scheduler (WorkManager, BGTaskScheduler).
- **Mech:** T `git grep -nIE 'kCLLocationAccuracyBest|PRIORITY_HIGH_ACCURACY|LocationAccuracy\.(best|high)|allowsBackgroundLocationUpdates|WakeLock|wakelock|Timer\.periodic|setInterval\(' -- ':!*test*' ':!*.md'`
- **Fix:** the lowest location accuracy and frequency the feature needs; schedule deferrable work with WorkManager or BGTaskScheduler; release wake locks in `finally`; stop timers when backgrounded.
- **Impact:** the OS flags the app for battery use, users uninstall it, and Android restricts its background work.
- **Source:** Android vitals, Excessive wake locks and background work; Apple, Energy Efficiency Guide for iOS Apps.

### MUX-01 [MEDIUM] Primary navigation outside the platform pattern
- **Detect:** a bottom navigation or tab bar with fewer than three or more than five destinations; icon-only tabs without labels; no visible selected state; primary destinations hidden in a drawer when three to five would fit the bar.
- **Mech:** T `git grep -nIE 'BottomNavigationBar|NavigationBar\(|CupertinoTabBar|TabView|UITabBarController|createBottomTabNavigator|BottomNavigation' -- ':!*.md'`
- **Fix:** three to five labelled destinations in the bar; more in an overflow screen or a navigation rail on large screens.
- **Impact:** users cannot see where they can go or where they are.
- **Source:** Least astonishment; Material Design 3, Navigation bar; Apple HIG, Tab bars.

