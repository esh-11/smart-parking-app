import 'package:flutter/material.dart';
import 'parking_slot_card.dart';
import 'booking_screen.dart';

class ParkingMapScreen extends StatefulWidget {
  const ParkingMapScreen({super.key});

  @override
  _ParkingMapScreenState createState() => _ParkingMapScreenState();
}

class _ParkingMapScreenState extends State<ParkingMapScreen> {
  final List<Map<String, dynamic>> _parkingSlots = [
    {'number': 'A1', 'zone': 'A', 'status': 'available'},
    {'number': 'A2', 'zone': 'A', 'status': 'occupied'},
    {'number': 'A3', 'zone': 'A', 'status': 'maintenance'},
    {'number': 'A4', 'zone': 'A', 'status': 'available'},
    {'number': 'B1', 'zone': 'B', 'status': 'occupied'},
    {'number': 'B2', 'zone': 'B', 'status': 'available'},
    {'number': 'B3', 'zone': 'B', 'status': 'available'},
    {'number': 'B4', 'zone': 'B', 'status': 'occupied'},
    {'number': 'C1', 'zone': 'C', 'status': 'available'},
    {'number': 'C2', 'zone': 'C', 'status': 'maintenance'},
    {'number': 'C3', 'zone': 'C', 'status': 'occupied'},
    {'number': 'C4', 'zone': 'C', 'status': 'available'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Parking Map')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search for parking... (e.g., A1, Zone B)',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10.0),
                ),
              ),
              onChanged: (value) {
                setState(() {
                  // simple client-side filter by slot number or zone
                });
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              children: const [
                _LegendDot(color: Color.fromARGB(255, 16, 212, 23), label: 'Available'),
                SizedBox(width: 12),
                _LegendDot(color: Color.fromARGB(255, 248, 46, 32), label: 'Occupied'),
                SizedBox(width: 12),
                _LegendDot(color: Color.fromARGB(255, 28, 152, 254), label: 'Maintenance'),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16.0),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 16.0,
                mainAxisSpacing: 16.0,
                childAspectRatio: 1.2,
              ),
              itemCount: _parkingSlots.length,
              itemBuilder: (context, index) {
                final slot = _parkingSlots[index];
                return ParkingSlotCard(
                  slot: slot,
                  onTap: () {
                    if ((slot['status'] ?? 'unknown') == 'available') {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => BookingScreen(slot: slot),
                        ),
                      );
                    }
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendDot extends StatelessWidget {
  final Color color;
  final String label;
  const _LegendDot({required this.color, required this.label});
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
