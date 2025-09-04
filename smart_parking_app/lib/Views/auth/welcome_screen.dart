import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'register_screen.dart';
import '../widgets/pf_logo.dart';

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  _WelcomeScreenState createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen>
    with TickerProviderStateMixin {
  late final PageController _pageController;
  int _currentPage = 0;
  late final AnimationController _animController;

  final List<Map<String, String>> _pages = const [
    {
      'title': 'Find the best\nparking spot',
      'subtitle': 'Real-time availability near you',
      'asset': 'assets/bg.jpg',
    },
    {
      'title': 'Book in seconds',
      'subtitle': 'Reserve before you arrive',
      'asset': 'assets/car.jpg',
    },
    {
      'title': 'Secure payments',
      'subtitle': 'Multiple methods, instant confirmation',
      'asset': 'assets/CD.jpg',
    },
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
    _animController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 650))
      ..forward();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF1F4F9),
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const PFLogo(size: 46),
                  TextButton(
                    onPressed: () {
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(builder: (_) => const LoginScreen()),
                      );
                    },
                    style: TextButton.styleFrom(
                      foregroundColor: const Color(0xFF2E5AAC),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 8),
                      backgroundColor:
                          const Color(0xFF2E5AAC).withOpacity(0.08),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text('Skip'),
                  ),
                ],
              ),
            ),

            // PageView with asset images
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (i) {
                  setState(() => _currentPage = i);
                  _animController
                    ..reset()
                    ..forward();
                },
                itemCount: _pages.length,
                itemBuilder: (_, index) {
                  final page = _pages[index];

                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Hero image with animated scale/fade and overlay
                        Expanded(
                          child: AnimatedBuilder(
                            animation: _animController,
                            builder: (context, child) {
                              final fade = Tween<double>(begin: 0.0, end: 1.0)
                                  .animate(CurvedAnimation(
                                      parent: _animController,
                                      curve: Curves.easeOut));
                              final scale = Tween<double>(begin: 0.96, end: 1.0)
                                  .animate(CurvedAnimation(
                                      parent: _animController,
                                      curve: Curves.easeOutCubic));

                              return ClipRRect(
                                borderRadius: BorderRadius.circular(20),
                                child: Stack(
                                  fit: StackFit.expand,
                                  children: [
                                    Transform.scale(
                                      scale: scale.value,
                                      child: FadeTransition(
                                        opacity: fade,
                                        child: Image.asset(
                                          page['asset']!,
                                          fit: BoxFit.cover,
                                        ),
                                      ),
                                    ),
                                    // Soft gradient overlay for text legibility
                                    Container(
                                      decoration: const BoxDecoration(
                                        gradient: LinearGradient(
                                          begin: Alignment.topCenter,
                                          end: Alignment.bottomCenter,
                                          colors: [
                                            Color(0x66000000),
                                            Color(0x11000000)
                                          ],
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            },
                          ),
                        ),

                        const SizedBox(height: 24),
                        // Title & subtitle
                        Text(
                          page['title']!,
                          style: theme.textTheme.headlineMedium?.copyWith(
                            fontSize: 30,
                            height: 1.2,
                            fontWeight: FontWeight.w800,
                            color: const Color(0xFF1F3B68),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          page['subtitle']!,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: const Color(0xFF546E7A),
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Dot indicators
                        Row(
                          children: List.generate(_pages.length, (dotIndex) {
                            final bool active = dotIndex == _currentPage;
                            return AnimatedContainer(
                              duration: const Duration(milliseconds: 300),
                              margin: const EdgeInsets.only(right: 12),
                              width: 14,
                              height: 14,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: active
                                    ? Colors.black
                                    : Colors.black.withOpacity(0.35),
                              ),
                            );
                          }),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),

            // Actions
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Get Started
                  Container(
                    height: 56,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(14),
                      gradient: const LinearGradient(
                        colors: [Color(0xFF2E5AAC), Color(0xFF6EA8FF)],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF2E5AAC).withOpacity(0.25),
                          blurRadius: 14,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(
                              builder: (_) => const RegisterScreen()),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.transparent,
                        shadowColor: Colors.transparent,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                      ),
                      child: const Text(
                        'Get Started',
                        style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: Colors.white),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Sign In
                  SizedBox(
                    height: 56,
                    child: OutlinedButton(
                      onPressed: () {
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(
                              builder: (_) => const LoginScreen()),
                        );
                      },
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(
                            color: Color(0xFF2E5AAC), width: 2),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                        backgroundColor: Colors.white,
                      ),
                      child: const Text(
                        'Sign In',
                        style: TextStyle(
                            color: Color(0xFF2E5AAC),
                            fontSize: 18,
                            fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Terms text
                  RichText(
                    textAlign: TextAlign.center,
                    text: const TextSpan(
                      style: TextStyle(
                          color: Color(0xFF546E7A), fontSize: 13, height: 1.5),
                      children: [
                        TextSpan(text: 'By continuing you agree to '),
                        TextSpan(
                            text: "Parking Flow's Terms of Service",
                            style: TextStyle(
                                color: Color(0xFF2E5AAC),
                                decoration: TextDecoration.underline,
                                fontWeight: FontWeight.w600)),
                        TextSpan(text: ' and '),
                        TextSpan(
                            text: 'Privacy Policy',
                            style: TextStyle(
                                color: Color(0xFF2E5AAC),
                                decoration: TextDecoration.underline,
                                fontWeight: FontWeight.w600)),
                        TextSpan(text: '.'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
