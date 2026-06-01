# APK Build & Deployment Guide

> Complete guide to build and deploy the Android Chat App

## Prerequisites

- Flutter SDK (3.0+)
- Android SDK (API level 21+)
- Java Development Kit (JDK 11+)
- Gradle (automatically included with Android SDK)

## Installation

### 1. Install Flutter
```bash
# Download Flutter from https://flutter.dev/docs/get-started/install

# Add Flutter to PATH
export PATH="$PATH:~/flutter/bin"

# Verify installation
flutter --version
flutter doctor
```

### 2. Install Android Studio & SDK

```bash
# Install Android Studio from https://developer.android.com/studio

# Set ANDROID_HOME
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"

# Accept Android licenses
flutter doctor --android-licenses
```

## Setup

### 1. Configure Server Connection

Edit `mobile/lib/config.dart`:

```dart
const String API_BASE_URL = 'http://192.168.x.x:8000'; // Your server IP
const String WS_BASE_URL = 'ws://192.168.x.x:8000';
```

### 2. Get Dependencies

```bash
cd mobile
flutter pub get
```

## Build APK

### Debug APK (for testing)
```bash
flutter build apk --debug
# Output: build/app/outputs/flutter-apk/app-debug.apk
```

### Release APK (for production)
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### App Bundle (for Google Play)
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

## Installation on Device

### Physical Device

```bash
# Enable USB Debugging on device
# Device Settings > Developer Options > USB Debugging

# Connect device via USB
adb devices

# Install APK
adb install build/app/outputs/flutter-apk/app-release.apk

# Run app
flutter run -d <device_id>
```

### Emulator

```bash
# Start emulator
emulator -avd <emulator_name>

# List connected devices
adb devices

# Install APK
adb install build/app/outputs/flutter-apk/app-release.apk

# Or run directly
flutter run
```

## Keystore Setup (for Google Play)

### Create Keystore

```bash
keytool -genkey -v -keystore ~/key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias chat_app
```

### Configure Gradle

Create `mobile/android/key.properties`:

```properties
storeFile=/path/to/key.jks
storePassword=your_store_password
keyPassword=your_key_password
keyAlias=chat_app
```

### Build Signed APK

```bash
flutter build apk --release
```

## Troubleshooting

### Connection Issues

1. **WebSocket Connection Failed**
   - Verify server is running: `curl http://192.168.x.x:8000/health`
   - Check firewall: `sudo ufw allow 8000`
   - Update config.dart with correct IP

2. **localhost Connection on Emulator**
   - Use `10.0.2.2` instead of `localhost` for emulator
   - This is the host machine's IP from Android emulator

### Build Errors

1. **Gradle Build Failed**
   ```bash
   flutter clean
   cd mobile/android && ./gradlew clean && cd ../..
   flutter pub get
   flutter build apk --release
   ```

2. **Permission Errors**
   ```bash
   chmod +x ~/flutter/bin/flutter
   chmod +x ~/Android/Sdk/platform-tools/adb
   ```

3. **Java Version Mismatch**
   ```bash
   export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
   ```

### Runtime Issues

1. **App Crashes**
   - Check logs: `flutter run -v`
   - Check server connectivity: `adb shell ping 8.8.8.8`

2. **WebSocket Disconnects**
   - Check network stability
   - Increase timeout in config.dart
   - Check server logs

## Deployment to Google Play

### Prerequisites

- Google Play Developer Account ($25 one-time fee)
- Signed APK or AAB

### Steps

1. Create app in Google Play Console
2. Prepare store listings and graphics
3. Build signed AAB: `flutter build appbundle --release`
4. Upload AAB to Google Play Console
5. Submit for review

## APK Signing

### Automatic Signing (Recommended)

```bash
# Generate signing key
keytool -genkey -v -keystore ~/key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias chat_app \
  -keypass password \
  -storepass password \
  -dname "CN=Your Name,O=Organization,L=City,ST=State,C=Country"

# Configure in key.properties
flutter build apk --release
```

### Manual Verification

```bash
# Verify signed APK
jarsigner -verify -verbose -certs \
  build/app/outputs/flutter-apk/app-release.apk
```

## Testing

### Unit Tests
```bash
flutter test
```

### Integration Tests
```bash
flutter test integration_test/
```

### Manual Testing Checklist

- [ ] Login/Register works
- [ ] Can join rooms
- [ ] Messages send/receive
- [ ] Connection drops handled gracefully
- [ ] Offline message queue works
- [ ] All UI elements responsive
- [ ] No crashes during normal use

## Release Checklist

- [ ] Update version in pubspec.yaml
- [ ] Update version code in build.gradle
- [ ] Test on multiple devices
- [ ] No debug logs in production
- [ ] All assets included
- [ ] Privacy policy updated
- [ ] Terms of service prepared
- [ ] Screenshots for store
- [ ] App description ready

## Performance Optimization

### Before Release

```bash
# Enable optimizations
flutter build apk --release --split-per-abi

# For better compression
flutter build appbundle --release
```

### File Size

```bash
# Check APK size
unzip -l build/app/outputs/flutter-apk/app-release.apk | tail -20

# Reduce size
flutter build apk --release --split-per-abi
```

## Support

For issues:
1. Check Flutter documentation: https://flutter.dev
2. Check Android documentation: https://developer.android.com
3. Review server logs
4. Check WebSocket connection
