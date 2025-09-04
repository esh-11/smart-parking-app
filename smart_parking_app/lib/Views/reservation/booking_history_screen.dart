import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class BookingHistoryScreen extends StatefulWidget {
  const BookingHistoryScreen({super.key});

  @override
  _BookingHistoryScreenState createState() => _BookingHistoryScreenState();
}

class _BookingHistoryScreenState extends State<BookingHistoryScreen> {
  final List<Map<String, dynamic>> _reservations = [
    {
      'id': '3',
      'slotNumber': 'A4',
      'date': DateTime(2023, 8, 20),
      'startTime': '09:00',
      'endTime': '12:00',
      'price': 15.0,
      'status': 'Completed',
      'zone': 'A',
    },
    {
      'id': '4',
      'slotNumber': 'B2',
      'date': DateTime(2023, 8, 18),
      'startTime': '14:00',
      'endTime': '18:00',
      'price': 20.0,
      'status': 'Completed',
      'zone': 'B',
    },
    {
      'id': '5',
      'slotNumber': 'A1',
      'date': DateTime(2023, 8, 15),
      'startTime': '10:00',
      'endTime': '13:00',
      'price': 15.0,
      'status': 'Completed',
      'zone': 'A',
    },
    {
      'id': '6',
      'slotNumber': 'C3',
      'date': DateTime(2023, 8, 10),
      'startTime': '11:00',
      'endTime': '15:00',
      'price': 20.0,
      'status': 'Completed',
      'zone': 'C',
    },
    {
      'id': '7',
      'slotNumber': 'B4',
      'date': DateTime(2023, 8, 5),
      'startTime': '09:00',
      'endTime': '17:00',
      'price': 40.0,
      'status': 'Completed',
      'zone': 'B',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF2D3748),
        title: const Text(
          'Booking History',
          style: TextStyle(
            color: Color(0xFF2D3748),
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded,
              color: Color(0xFF2D3748)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _reservations.isEmpty
          ? const Center(
              child: Text('No booking history'),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: _reservations.length,
              itemBuilder: (context, index) {
                final reservation = _reservations[index];
                return HistoryCard(reservation: reservation);
              },
            ),
    );
  }
}

class HistoryCard extends StatelessWidget {
  final Map<String, dynamic> reservation;

  const HistoryCard({
    super.key,
    required this.reservation,
  });

  @override
  Widget build(BuildContext context) {
    final formattedDate = DateFormat.yMMMd().format(reservation['date']);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Slot ${reservation['slotNumber']} (Zone ${reservation['zone']})',
                  style: const TextStyle(
                      fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  'RS ${reservation['price'].toStringAsFixed(2)}',
                  style: const TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 18),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text('Date: $formattedDate'),
            const SizedBox(height: 5),
            Text(
                'Time: ${reservation['startTime']} - ${reservation['endTime']}'),
            const SizedBox(height: 5),
            Row(
              children: [
                const Text('Status: '),
                Chip(
                  label: Text(
                    reservation['status'],
                    style: const TextStyle(color: Colors.white),
                  ),
                  backgroundColor: reservation['status'] == 'Completed'
                      ? Colors.green
                      : Colors.blue,
                ),
              ],
            ),
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Receipt sent to your email'),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                child: const Text('Download Receipt'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
