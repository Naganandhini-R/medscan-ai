import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import {
  LogOut,
  Bell,
  ShieldCheck,
  Scan,
  History,
  User,
  Archive,
  ChevronRight,
  FlaskConical,
  AlertTriangle,
  Clock,
  BookOpen,
  AlertCircle,
  CheckCircle2,
  Image as ImageIcon,
} from 'lucide-react-native';
import { launchImageLibrary } from 'react-native-image-picker';
import { Alert } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors } from '../theme/Colors';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { getStats, getRecentScans, ScanResult } from '../services/api.service';
import { translations, Language } from '../utils/translations';

const HomeScreen = ({ navigation }: any) => {
  const [userName, setUserName] = useState('User');
  const [stats, setStats] = useState({
    total_scans: 0,
    fake_detected: 0,
    genuine: 0,
  });
  const [recentScans, setRecentScans] = useState<ScanResult[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<Language>('en');

  const t = translations[language];

  useFocusEffect(
    useCallback(() => {
      loadUser();
      loadDashboardData();
      loadSettings();
    }, []),
  );

  const loadSettings = async () => {
    try {
      const savedMode = await AsyncStorage.getItem('darkMode');
      if (savedMode !== null) {
        setIsDarkMode(JSON.parse(savedMode));
      }
      const savedLang = await AsyncStorage.getItem('language');
      if (savedLang !== null) {
        setLanguage(savedLang as Language);
      }
    } catch (e) {
      console.log('Error loading settings', e);
    }
  };

  const loadDashboardData = async () => {
    try {
      const userJson = await AsyncStorage.getItem('user');
      let userId = undefined;
      if (userJson) {
        userId = JSON.parse(userJson).id;
      }
      const [s, r] = await Promise.all([getStats(userId), getRecentScans(3, userId)]);
      setStats(s);
      setRecentScans(r);
    } catch (error) {
      console.error('Failed to load dashboard data', error);
    }
  };

  const loadUser = async () => {
    try {
      const userJson = await AsyncStorage.getItem('user');
      if (userJson) {
        const user = JSON.parse(userJson);
        // Try to find the name in various common properties
        setUserName(
          user.full_name || user.name || user.email?.split('@')[0] || 'User',
        );
      }
    } catch (e) {
      console.log('Error loading user', e);
    }
  };

  const pickImageAndNavigate = async () => {
    try {
      const result = await launchImageLibrary({
        mediaType: 'photo',
        quality: 0.8,
        includeExtra: true,
        selectionLimit: 3, // Enable picking up to 3 photos
      });

      if (result.didCancel) return;
      if (result.errorCode) {
        Alert.alert('Error', result.errorMessage || 'Failed to pick image');
        return;
      }

      if (result.assets && result.assets.length > 0) {
        const pickedImages: any = {};
        if (result.assets[0]) pickedImages.front = result.assets[0].uri;
        if (result.assets[1]) pickedImages.back = result.assets[1].uri;
        if (result.assets[2]) pickedImages.composition = result.assets[2].uri;

        navigation.navigate('Review', {
          images: pickedImages,
        });
      }
    } catch (error) {
      console.error('Pick Image Error:', error);
      Alert.alert('Error', 'An unexpected error occurred.');
    }
  };

  const themeStyles = {
    container: { backgroundColor: isDarkMode ? '#0F172A' : '#F8FAFC' },
    text: { color: isDarkMode ? '#F8FAFC' : Colors.textHeader },
    subText: { color: isDarkMode ? '#94A3B8' : Colors.textSub },
    card: {
      backgroundColor: isDarkMode ? '#1E293B' : '#FFF',
      borderColor: isDarkMode ? '#334155' : '#F1F5F9',
    },
    iconBtn: { backgroundColor: isDarkMode ? '#1E293B' : '#FFF' },
  };

  return (
    <SafeAreaView style={[styles.container, themeStyles.container]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#0F172A' : '#F8FAFC'}
      />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <View>
            <Text style={[styles.greeting, themeStyles.text]}>
              {t.hello}, {userName}
            </Text>
            <Text style={[styles.subGreeting, themeStyles.subText]}>
              {t.welcome}
            </Text>
          </View>
          <View style={styles.headerIcons}>
            <TouchableOpacity
              style={[styles.iconBtn, themeStyles.iconBtn]}
              onPress={() => {
                AsyncStorage.clear();
                navigation.replace('Login');
              }}>
              <LogOut size={24} color={Colors.error} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Main Scan Button */}
        <TouchableOpacity
          style={styles.scanButton}
          onPress={() => navigation.navigate('Scan')}>
          <LinearGradient
            colors={['#2196F3', '#0D47A1']}
            style={styles.scanBtnGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}>
            <View style={styles.scanContent}>
              <View style={styles.scanIconContainer}>
                <Scan color="#FFF" size={32} />
              </View>
              <View>
                <Text style={styles.scanBtnText}>{t.startAIScan}</Text>
                <Text style={styles.scanBtnSub}>{t.verifyNow}</Text>
              </View>
            </View>
            <ChevronRight color="#FFF" size={24} />
          </LinearGradient>
        </TouchableOpacity>

        {/* Quick Stats / Action Cards */}
        <View style={styles.statsRow}>
          <TouchableOpacity
            style={[
              styles.smallCard,
              { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' },
            ]}
            onPress={() => navigation.navigate('Cabinet')}>
            <Archive color={Colors.primary} size={24} />
            <Text style={[styles.smallCardTitle, themeStyles.text]}>
              {t.myCabinet}
            </Text>
            <Text style={[styles.smallCardSub, themeStyles.subText]}>
              {stats.total_scans} {t.totalScans}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.smallCard,
              { backgroundColor: isDarkMode ? '#1E293B' : '#ECFDF5' },
            ]}
            onPress={() => navigation.navigate('SafetyCenter')}>
            <BookOpen color={Colors.success} size={24} />
            <Text style={[styles.smallCardTitle, themeStyles.text]}>
              {t.safetyCenter}
            </Text>
            <Text style={[styles.smallCardSub, themeStyles.subText]}>
              {t.verifiedInfo}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Recent Scans */}
        <View style={styles.recentHeader}>
          <Text style={[styles.sectionTitle, themeStyles.text]}>
            {t.recentScans}
          </Text>
          <TouchableOpacity onPress={() => navigation.navigate('History')}>
            <Text style={styles.seeAll}>{t.seeAll}</Text>
          </TouchableOpacity>
        </View>

        <View style={[styles.recentList]}>
          {recentScans.length > 0 ? (
            recentScans.map(scan => (
              <TouchableOpacity
                key={scan.id}
                style={[styles.scanCard, themeStyles.card]}
                onPress={() =>
                  navigation.navigate('Result', { scanId: scan.id })
                }>
                <View
                  style={[
                    styles.iconBox,
                    {
                      backgroundColor:
                        scan.status === 'GENUINE'
                          ? isDarkMode
                            ? '#064E3B'
                            : '#ECFDF5'
                          : scan.status === 'SUSPICIOUS'
                            ? isDarkMode
                              ? '#451A03'
                              : '#FFFBEB'
                            : isDarkMode
                              ? '#450A0A'
                              : '#FEF2F2',
                    },
                  ]}>
                  {scan.status === 'GENUINE' ? (
                    <ShieldCheck size={24} color={Colors.success} />
                  ) : scan.status === 'SUSPICIOUS' ? (
                    <Clock size={24} color={Colors.warning} />
                  ) : (
                    <AlertCircle size={24} color={Colors.error} />
                  )}
                </View>
                <View style={styles.scanInfo}>
                  <Text style={[styles.scanName, themeStyles.text]}>
                    {scan.medicine_name || 'Generic Medicine'}
                  </Text>
                  <Text style={[styles.scanDate, themeStyles.subText]}>
                    {new Date().toLocaleDateString()} • {scan.status}
                  </Text>
                </View>
                <ChevronRight
                  size={20}
                  color={isDarkMode ? '#94A3B8' : Colors.textSub}
                />
              </TouchableOpacity>
            ))
          ) : (
            <Text
              style={[
                { color: Colors.textSub, fontStyle: 'italic' },
                themeStyles.subText,
              ]}>
              {t.noScans}
            </Text>
          )}
        </View>

        <View style={styles.tipsSection}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, themeStyles.text]}>
              {t.safetyCenter}
            </Text>
            <TouchableOpacity
              onPress={() => navigation.navigate('SafetyCenter')}>
              <Text style={styles.seeAllText}>{t.stayAlert}</Text>
            </TouchableOpacity>
          </View>
          <TouchableOpacity
            style={[styles.tipCard, themeStyles.card]}
            onPress={() => navigation.navigate('SafetyCenter')}>
            <View
              style={[
                styles.tipIcon,
                { backgroundColor: isDarkMode ? '#334155' : '#EFF6FF' },
              ]}>
              <BookOpen size={20} color={Colors.primary} />
            </View>
            <Text style={[styles.tipText, themeStyles.text]}>{t.tipText}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Bottom Navigation Mock */}
      <View
        style={[
          styles.bottomTab,
          themeStyles.card,
          { borderTopColor: isDarkMode ? '#334155' : '#F1F5F9' },
        ]}>
        <TouchableOpacity style={styles.tabItem}>
          <View style={styles.activeTabCircle}>
            <ShieldCheck size={24} color={Colors.primary} />
          </View>
          <Text style={[styles.tabText, { color: Colors.primary }]}>
            {t.home}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={pickImageAndNavigate}>
          <ImageIcon
            size={24}
            color={isDarkMode ? '#94A3B8' : Colors.textSub}
          />
          <Text style={[styles.tabText, themeStyles.subText]}>Upload</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => navigation.navigate('History')}>
          <History size={24} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
          <Text style={[styles.tabText, themeStyles.subText]}>{t.history}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => navigation.navigate('Profile')}>
          <User size={24} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
          <Text style={[styles.tabText, themeStyles.subText]}>{t.profile}</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  scrollContent: { padding: 20, paddingBottom: 100 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 25,
  },
  greeting: { fontSize: 24, fontWeight: 'bold', color: Colors.textHeader },
  subGreeting: { fontSize: 14, color: Colors.textSub, marginTop: 4 },
  headerIcons: { flexDirection: 'row', gap: 12 },
  iconBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
  },

  scanButton: {
    height: 100,
    borderRadius: 24,
    overflow: 'hidden',
    elevation: 8,
    marginBottom: 25,
  },
  scanBtnGradient: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  scanContent: { flexDirection: 'row', alignItems: 'center' },
  scanIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  scanBtnText: { color: '#FFF', fontSize: 20, fontWeight: 'bold' },
  scanBtnSub: { color: 'rgba(255,255,255,0.8)', fontSize: 12 },

  statsRow: { flexDirection: 'row', gap: 15, marginBottom: 25 },
  smallCard: { flex: 1, padding: 20, borderRadius: 24, elevation: 2 },
  smallCardTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginTop: 12,
  },
  smallCardSub: { fontSize: 12, color: Colors.textSub, marginTop: 4 },

  recentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
  seeAll: { color: Colors.primary, fontWeight: '600' },
  recentList: { gap: 12, marginBottom: 25 },
  scanCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 15,
    borderRadius: 20,
    elevation: 1,
  },
  iconBox: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  scanInfo: { flex: 1 },
  scanName: { fontSize: 16, fontWeight: 'bold', color: Colors.textHeader },
  scanDate: { fontSize: 12, color: Colors.textSub, marginTop: 2 },
  statusBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  statusText: { fontSize: 12, fontWeight: '600' },

  tipsSection: { marginBottom: 25 },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  seeAllText: { color: Colors.primary, fontSize: 14, fontWeight: 'bold' },
  tipCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 18,
    borderRadius: 20,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  tipIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  tipText: { flex: 1, color: Colors.textHeader, fontSize: 14, fontWeight: '500' },

  bottomTab: {
    height: 70,
    backgroundColor: '#FFF',
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    position: 'absolute',
    bottom: 0,
    width: '100%',
    paddingHorizontal: 20,
  },
  tabItem: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  activeTabCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 2,
  },
  tabText: { fontSize: 10, fontWeight: '600', color: Colors.textSub },
});

export default HomeScreen;
