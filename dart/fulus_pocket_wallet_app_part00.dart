  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.4.0
  sqflite: ^2.3.0
  path: ^1.8.0
  qr_flutter: ^4.0.0
  intl: ^0.18.0
  cupertino_icons: ^1.0.6

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true

// SIMULATION PURE – AUCUNE TRANSACTION RÉELLE
// Conformément à l'article L111-1 du Code monétaire et financier,
// l'euro est la seule monnaie ayant cours légal en France.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/wallet/presentation/wallet_page.dart';
import 'features/zakat/presentation/zakat_calculator.dart';
import 'features/crd/presentation/price_floor_page.dart';
import 'features/bassira/presentation/early_warning_page.dart';

void main() {
  runApp(ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fulus Pocket (Simulation)',
      theme: ThemeData(primarySwatch: Colors.green),
      initialRoute: '/',
      routes: {
        '/': (context) => HomePage(),
        '/wallet': (context) => WalletPage(),
        '/zakat': (context) => ZakatCalculatorPage(),
        '/crd': (context) => PriceFloorPage(),
        '/bassira': (context) => EarlyWarningPage(),
      },
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Fulus Pocket'), backgroundColor: Colors.green[900]),
      body: ListView(
        children: [
          ListTile(
            leading: Icon(Icons.account_balance_wallet),
            title: Text('Portefeuille'),
            onTap: () => Navigator.pushNamed(context, '/wallet'),
          ),
          ListTile(
            leading: Icon(Icons.calculate),
            title: Text('Calculateur Zakat'),
            onTap: () => Navigator.pushNamed(context, '/zakat'),
          ),
          ListTile(
            leading: Icon(Icons.trending_up),
            title: Text('CRD – Grondona'),
            onTap: () => Navigator.pushNamed(context, '/crd'),
          ),
          ListTile(
            leading: Icon(Icons.warning),
            title: Text('Bassira – Signaux faibles'),
            onTap: () => Navigator.pushNamed(context, '/bassira'),
          ),
          SizedBox(height: 40),
          Container(
            padding: EdgeInsets.all(16),
            color: Colors.grey[200],
            child: Text(
              "⚠️ SIMULATION PURE – Aucune transaction réelle\n"
              "Aucun fulus émis – Aucune collecte de Zakat\n"
              "L'euro est la seule monnaie ayant cours légal.",
              style: TextStyle(fontSize: 12, color: Colors.red),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}

lib/features/wallet/domain/transaction.dart (Entité)
class Transaction {
  final String fromUserId;
  final String toUserId;
  final int amount;
  final String good;
  final int logisticsDelayDays;
  final bool inspectedByMuhtassib;
  final DateTime timestamp;

  Transaction({
    required this.fromUserId,
    required this.toUserId,
    required this.amount,
    required this.good,
    required this.logisticsDelayDays,
    required this.inspectedByMuhtassib,
    required this.timestamp,
  });
}
lib/features/wallet/infrastructure/mock_api.dart (API simulée)
import '../domain/transaction.dart';

class MockApi {
  Future<int> getBalance() async {
    await Future.delayed(Duration(milliseconds: 300));
    return 1250; // solde fictif
  }

  Future<List<Transaction>> getTransactions() async {
    await Future.delayed(Duration(milliseconds: 400));
    return [
      Transaction(
        fromUserId: "boulangerie",
        toUserId: "moi",
        amount: 30,
        good: "pain",
        logisticsDelayDays: 1,
        inspectedByMuhtassib: true,
        timestamp: DateTime.now().subtract(Duration(hours: 2)),
      ),
      Transaction(
        fromUserId: "moi",
        toUserId: "epicier",
        amount: 20,
        good: "légumes",
        logisticsDelayDays: 0,
        inspectedByMuhtassib: false,
        timestamp: DateTime.now().subtract(Duration(days: 1)),
      ),
    ];
  }

  Future<bool> sendFulus(String to, int amount) async {
    await Future.delayed(Duration(milliseconds: 500));
    // aucune transaction réelle
    return true;
  }
}
lib/features/wallet/presentation/wallet_page.dart (UI)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/transaction.dart';
import '../infrastructure/mock_api.dart';

final walletProvider = StateNotifierProvider<WalletNotifier, WalletState>((ref) {
  return WalletNotifier();
});

class WalletState {
  final int fulusBalance;
  final List<Transaction> transactions;
  final bool isLoading;
  WalletState({required this.fulusBalance, required this.transactions, this.isLoading = false});
}

class WalletNotifier extends StateNotifier<WalletState> {
  WalletNotifier() : super(WalletState(fulusBalance: 1250, transactions: [])) {
    loadTransactions();
  }

  final MockApi _api = MockApi();

  Future<void> loadTransactions() async {
    state = WalletState(fulusBalance: state.fulusBalance, transactions: state.transactions, isLoading: true);
    final txs = await _api.getTransactions();
    state = WalletState(fulusBalance: state.fulusBalance, transactions: txs, isLoading: false);
  }

  Future<void> sendFulus(String to, int amount) async {
    state = WalletState(fulusBalance: state.fulusBalance, transactions: state.transactions, isLoading: true);
    final success = await _api.sendFulus(to, amount);
    if (success) {
      final newBalance = state.fulusBalance - amount;
      final newTx = Transaction(
        fromUserId: "moi",
        toUserId: to,
        amount: amount,
        good: "transfert",
        logisticsDelayDays: 0,
        inspectedByMuhtassib: false,
        timestamp: DateTime.now(),
      );
      state = WalletState(
        fulusBalance: newBalance,
        transactions: [newTx, ...state.transactions],
        isLoading: false,
      );
    } else {
      state = WalletState(fulusBalance: state.fulusBalance, transactions: state.transactions, isLoading: false);
    }
  }
}

class WalletPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final walletState = ref.watch(walletProvider);
    final notifier = ref.read(walletProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: Text('Fulus Pocket'), backgroundColor: Colors.green[900]),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            BalanceWidget(balance: walletState.fulusBalance),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                notifier.sendFulus("guilde_mecano", 50);
              },
              child: Text("Envoyer 50 fulus (simulation)"),
            ),
            SizedBox(height: 20),
            Expanded(
              child: ListView.builder(
                itemCount: walletState.transactions.length,
                itemBuilder: (context, index) {
                  final tx = walletState.transactions[index];
                  return ListTile(
                    title: Text('${tx.amount} fulus - ${tx.good}'),
                    subtitle: Text('De: ${tx.fromUserId} à: ${tx.toUserId}'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class BalanceWidget extends StatelessWidget {
  final int balance;
  const BalanceWidget({required this.balance});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text('Solde en fulus', style: TextStyle(fontSize: 16)),
            Text('$balance', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

lib/features/zakat/domain/zakat.dart (Logique)
class Zakat {
  // Calcul selon la règle : 2.5% sur or/argent et profits
  static double calculate({
    required double goldGrams,
    required double silverGrams,
    required double tradeProfit,
  }) {
    // Conversion simplifiée : 1g or = 1 unité nuqud, 1g argent = 0.05 unité nuqud
    const silverToGoldRatio = 0.05;
    final totalNuqud = goldGrams + (silverGrams * silverToGoldRatio) + tradeProfit;
    return totalNuqud * 0.025;
  }
}
lib/features/zakat/presentation/zakat_calculator.dart (UI)
import 'package:flutter/material.dart';
import '../domain/zakat.dart';

class ZakatCalculatorPage extends StatefulWidget {
  @override
  _ZakatCalculatorPageState createState() => _ZakatCalculatorPageState();
}

class _ZakatCalculatorPageState extends State<ZakatCalculatorPage> {
  final _goldController = TextEditingController(text: "100");
  final _silverController = TextEditingController(text: "500");
  final _profitController = TextEditingController(text: "50");
  double _result = 0.0;

  void _calculate() {
    final gold = double.tryParse(_goldController.text) ?? 0;
    final silver = double.tryParse(_silverController.text) ?? 0;
    final profit = double.tryParse(_profitController.text) ?? 0;

    setState(() {
      _result = Zakat.calculate(goldGrams: gold, silverGrams: silver, tradeProfit: profit);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Calculateur Zakat (simulation)"),
        backgroundColor: Colors.green[900],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _goldController,
              decoration: InputDecoration(labelText: "Or (grammes)"),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _silverController,
              decoration: InputDecoration(labelText: "Argent (grammes)"),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _profitController,
              decoration: InputDecoration(labelText: "Profit commercial (équivalent nuqud)"),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _calculate,
              child: Text("Calculer la Zakat"),
            ),
            SizedBox(height: 20),
            Text(
              "Zakat due : ${_result.toStringAsFixed(2)} (en nuqud)",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            Container(
              padding: EdgeInsets.all(12),
              color: Colors.grey[200],
              child: Text(
                "⚠️ Simulation uniquement. Aucune collecte réelle n'est effectuée.",
                style: TextStyle(fontSize: 12, color: Colors.red),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

lib/features/crd/domain/grondona.dart (Logique)
class Commodity {
  final String name;
  final double floorPrice;
  final double ceilingPrice;
  double currentPrice;

  Commodity({
    required this.name,
    required this.floorPrice,
    required this.ceilingPrice,
    required this.currentPrice,
  });
}

class GrondonaSystem {
  final List<Commodity> _commodities = [];

  GrondonaSystem() {
    _initDemoData();
  }

  void _initDemoData() {
    _commodities.addAll([
      Commodity(name: "Blé", floorPrice: 10.0, ceilingPrice: 20.0, currentPrice: 14.5),
      Commodity(name: "Cuivre", floorPrice: 5.0, ceilingPrice: 12.0, currentPrice: 8.2),
      Commodity(name: "Sel", floorPrice: 2.0, ceilingPrice: 6.0, currentPrice: 3.8),
    ]);
  }

  List<Commodity> getAllCommodities() => _commodities;

  void updateCurrentPrice(String name, double newPrice) {
    final commodity = _commodities.firstWhere((c) => c.name == name);
    if (newPrice < commodity.floorPrice) {
      // simulation : déclenchement achat CRD
      commodity.currentPrice = commodity.floorPrice;
    } else if (newPrice > commodity.ceilingPrice) {
      // simulation : déclenchement vente CRD
      commodity.currentPrice = commodity.ceilingPrice;
    } else {
      commodity.currentPrice = newPrice;
    }
  }
}
lib/features/crd/presentation/price_floor_page.dart (UI)
import 'package:flutter/material.dart';
import '../domain/grondona.dart';

class PriceFloorPage extends StatefulWidget {
  @override
  _PriceFloorPageState createState() => _PriceFloorPageState();
}

class _PriceFloorPageState extends State<PriceFloorPage> {
  final List<Map<String, dynamic>> _commodities = [];
  final GrondonaSystem _grondona = GrondonaSystem();

  @override
  void initState() {
    super.initState();
    _loadCommodities();
  }

  void _loadCommodities() {
    _commodities.clear();
    for (var commodity in _grondona.getAllCommodities()) {
      _commodities.add({
        "name": commodity.name,
        "floorPrice": commodity.floorPrice,
        "ceilingPrice": commodity.ceilingPrice,
        "currentPrice": commodity.currentPrice,
      });
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("CRD – Grondona System (simulation)"),
        backgroundColor: Colors.green[900],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              "Prix plancher / plafond simulés",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _commodities.length,
              itemBuilder: (context, index) {
                final c = _commodities[index];
                return Card(
                  margin: EdgeInsets.all(8),
                  child: ListTile(
                    title: Text(c["name"]),
                    subtitle: Text(
                      "Plancher: ${c["floorPrice"]} fulus | Plafond: ${c["ceilingPrice"]} fulus\n"
                      "Prix courant simulé: ${c["currentPrice"]} fulus",
                    ),
                    trailing: Icon(Icons.trending_up),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: EdgeInsets.all(12),
            color: Colors.grey[200],
            child: Text(
              "⚠️ Simulation du système Grondona. Aucun stock réel n'est détenu.",
              style: TextStyle(fontSize: 12, color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}

lib/features/bassira/domain/signal.dart
enum SignalCategory { Logistics, Muhtassib, Social }

class EarlySignal {
  final String description;
  final double confidence; // 0.0 → 1.0 (simulé)
  final SignalCategory category;

  EarlySignal({
    required this.description,
    required this.confidence,
    required this.category,
  });
}
lib/features/bassira/presentation/early_warning_page.dart
import 'package:flutter/material.dart';
import '../domain/signal.dart';

class EarlyWarningPage extends StatefulWidget {
  @override
  _EarlyWarningPageState createState() => _EarlyWarningPageState();
}

class _EarlyWarningPageState extends State<EarlyWarningPage> {
  final List<EarlySignal> _signals = [];

  @override
  void initState() {
    super.initState();
    _loadSignals();
  }

  void _loadSignals() {
    _signals.clear();
    _signals.addAll([
      EarlySignal(
        description: "Retards de paiement récurrents chez 3 commerçants du souk",
        confidence: 0.7,
        category: SignalCategory.Logistics,
      ),
      EarlySignal(
        description: "Rumeur de coupure de la route de Zahlé – surveiller les stocks",
        confidence: 0.5,
        category: SignalCategory.Logistics,
      ),
      EarlySignal(
        description: "Plusieurs plaintes pour poids non conformes",
        confidence: 0.8,
        category: SignalCategory.Muhtassib,
      ),
      EarlySignal(
        description: "Baisse de fréquentation du souk – 15% sur deux semaines",
        confidence: 0.6,
        category: SignalCategory.Social,
      ),
    ]);
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Bassira – Signaux faibles (simulation)"),
        backgroundColor: Colors.green[900],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              "Ces signaux ne sont pas des prédictions. Ce sont des alertes narratives simulées.",
              style: TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _signals.length,
              itemBuilder: (context, index) {
                final s = _signals[index];
                return Card(
                  margin: EdgeInsets.all(8),
                  color: _getColorForCategory(s.category),
                  child: ListTile(
                    title: Text(s.description),
                    subtitle: Text("Confiance simulée: ${(s.confidence * 100).toInt()}%"),
                    leading: _getIconForCategory(s.category),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: EdgeInsets.all(12),
            color: Colors.grey[200],
            child: Text(
              "⚠️ Bassira simulée. Aucune IA prédictive réelle.",
              style: TextStyle(fontSize: 12, color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  Color _getColorForCategory(SignalCategory category) {
    switch (category) {
      case SignalCategory.Logistics:
        return Colors.orange[50]!;
      case SignalCategory.Muhtassib:
        return Colors.red[50]!;
      case SignalCategory.Social:
        return Colors.blue[50]!;
      default:
        return Colors.grey[50]!;
    }
  }

  Icon _getIconForCategory(SignalCategory category) {
    switch (category) {
      case SignalCategory.Logistics:
        return Icon(Icons.local_shipping);
      case SignalCategory.Muhtassib:
        return Icon(Icons.scale);
      case SignalCategory.Social:
        return Icon(Icons.people);
      default:
        return Icon(Icons.warning);
    }
  }
}
