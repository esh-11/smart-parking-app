class UserData {
  static Map<String, dynamic> _userData = {
    'name': 'John David',
    'email': 'johndavid@gmail.com',
    'phone': '+94 765923452',
    'vehicle': 'CAE-4326',
    'license': 'D123456789',
    'profileImage': null, // file path (mobile/desktop)
    'profileImageBase64': null, // base64-encoded bytes (web-safe)
  };

  static Map<String, dynamic> get userData => _userData;

  static String get name => _userData['name'] ?? 'User';

  static String get email => _userData['email'] ?? '';

  static String get phone => _userData['phone'] ?? '';

  static String get vehicle => _userData['vehicle'] ?? '';

  static void updateUserData(Map<String, dynamic> newData) {
    _userData.addAll(newData);
  }

  static void setProfileImage(String? imagePath) {
    _userData['profileImage'] = imagePath;
  }

  static void setProfileImageBase64(String? base64) {
    _userData['profileImageBase64'] = base64;
  }

  static String? getProfileImage() {
    return _userData['profileImage'];
  }

  static String? getProfileImageBase64() {
    return _userData['profileImageBase64'];
  }

  static void clearUserData() {
    _userData = {
      'name': 'John David',
      'email': 'johndavid@gmail.com',
      'phone': '+94 765923452',
      'vehicle': 'CAE-4326',
      'license': 'D123456789',
      'profileImage': null,
      'profileImageBase64': null,
    };
  }
}
