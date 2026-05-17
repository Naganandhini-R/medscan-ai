import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import {
  ArrowLeft,
  ShieldCheck,
  CheckCircle2,
  ShieldAlert,
  Cpu,
  Database,
} from 'lucide-react-native';
import {Colors} from '../theme/Colors';
import LinearGradient from 'react-native-linear-gradient';

export default function SafetyCenterScreen({navigation}: any) {
  const safetySteps = [
    {
      icon: <Cpu size={24} color={Colors.primary} />,
      title: 'AI Vision Check',
      desc: 'Our AI analyzes the packaging patterns, holograms, and font consistency to detect clones.',
    },
    {
      icon: <Database size={24} color={Colors.success} />,
      title: 'Blockchain Registry',
      desc: "We verify the unique batch number against the manufacturer's decentralized ledger.",
    },
    {
      icon: <ShieldCheck size={24} color={Colors.primary} />,
      title: 'Registry Validation',
      desc: 'Official medical databases like FDA and National Registries are used to verify ingredients.',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backBtn}>
          <ArrowLeft size={24} color={Colors.textHeader} />
        </TouchableOpacity>
        <Text style={styles.title}>Safety Center</Text>
        <View style={{width: 44}} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.heroSection}>
          <LinearGradient
            colors={['#ECFDF5', '#F0FDFA']}
            style={styles.heroGradient}>
            <ShieldCheck size={48} color={Colors.success} />
            <Text style={styles.heroTitle}>Your Health, Verified</Text>
            <Text style={styles.heroSub}>
              MedScan AI uses a multi-layer verification system to ensure every
              medicine you take is 100% genuine.
            </Text>
          </LinearGradient>
        </View>

        <Text style={styles.sectionTitle}>How we protect you</Text>

        {safetySteps.map((step, index) => (
          <View key={index} style={styles.stepCard}>
            <View style={styles.iconContainer}>{step.icon}</View>
            <View style={styles.stepInfo}>
              <Text style={styles.stepTitle}>{step.title}</Text>
              <Text style={styles.stepDesc}>{step.desc}</Text>
            </View>
          </View>
        ))}

        <View style={styles.alertBox}>
          <ShieldAlert size={20} color={Colors.error} />
          <Text style={styles.alertText}>
            Always report suspicious medicines immediately to help protect your
            community.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#F8FAFC'},
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFF',
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {fontSize: 20, fontWeight: 'bold', color: Colors.textHeader},
  scrollContent: {padding: 20},
  heroSection: {
    borderRadius: 24,
    overflow: 'hidden',
    marginBottom: 30,
    elevation: 2,
  },
  heroGradient: {padding: 25, alignItems: 'center', textAlign: 'center'},
  heroTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginTop: 15,
  },
  heroSub: {
    fontSize: 14,
    color: Colors.textSub,
    textAlign: 'center',
    marginTop: 10,
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginBottom: 20,
  },
  stepCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 12,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  stepInfo: {flex: 1},
  stepTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginBottom: 4,
  },
  stepDesc: {fontSize: 13, color: Colors.textSub, lineHeight: 18},
  alertBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: '#FEF2F2',
    padding: 15,
    borderRadius: 16,
    marginTop: 10,
  },
  alertText: {flex: 1, fontSize: 12, color: Colors.error, fontWeight: '500'},
});
