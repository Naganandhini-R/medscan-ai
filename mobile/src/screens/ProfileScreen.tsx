import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Image,
  Switch,
  StatusBar,
  Alert,
  Modal,
} from 'react-native';
import {
  Bell,
  ChevronRight,
  Moon,
  Globe,
  Shield,
  HelpCircle,
  Info,
  LogOut,
  User as UserIcon,
  ShieldCheck,
  Image as ImageIcon,
  History as HistoryIcon,
  X,
  Check,
} from 'lucide-react-native';
import { launchImageLibrary } from 'react-native-image-picker';
import { Colors } from '../theme/Colors';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { translations, Language } from '../utils/translations';

const ProfileOption = ({
  icon: Icon,
  label,
  value,
  onPress,
  showSwitch,
  switchValue,
  onSwitchChange,
  isDarkMode,
}: any) => (
  <TouchableOpacity style={styles.optionRow} onPress={onPress}>
    <View
      style={[
        styles.optionIconBox,
        isDarkMode && { backgroundColor: '#334155' },
      ]}>
      <Icon size={20} color={isDarkMode ? '#F8FAFC' : Colors.textHeader} />
    </View>
    <Text style={[styles.optionLabel, isDarkMode && { color: '#F8FAFC' }]}>
      {label}
    </Text>
    {value && (
      <Text style={[styles.optionValue, isDarkMode && { color: '#94A3B8' }]}>
        {value}
      </Text>
    )}
    {showSwitch ? (
      <Switch
        value={switchValue}
        onValueChange={onSwitchChange}
        trackColor={{ false: '#E2E8F0', true: Colors.primary }}
        thumbColor="#FFF"
      />
    ) : (
      <ChevronRight size={18} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
    )}
  </TouchableOpacity>
);

const ProfileScreen = ({ navigation }: any) => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [user, setUser] = useState({ name: 'User', email: 'user@example.com', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=150' });
  const [showLangModal, setShowLangModal] = useState(false);

  const t = translations[language];

  useFocusEffect(
    useCallback(() => {
      loadUser();
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

  const loadUser = async () => {
    try {
      const userJson = await AsyncStorage.getItem('user');
      if (userJson) {
        const userData = JSON.parse(userJson);
        setUser({
          name: userData.full_name || userData.name || 'User',
          email: userData.email || 'user@example.com',
          avatar: userData.avatar || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=150',
        });
      }
    } catch (e) {
      console.log('Error loading user profile', e);
    }
  };

  const toggleDarkMode = async (value: boolean) => {
    setIsDarkMode(value);
    try {
      await AsyncStorage.setItem('darkMode', JSON.stringify(value));
    } catch (e) {
      console.log('Error saving dark mode', e);
    }
  };

  const selectLanguage = async (nextLang: Language) => {
    setLanguage(nextLang);
    setShowLangModal(false);
    try {
      await AsyncStorage.setItem('language', nextLang);
    } catch (e) {
      console.log('Error saving language', e);
    }
  };

  const openLanguageModal = () => {
    setShowLangModal(true);
  };

  const handleLogout = async () => {
    await AsyncStorage.clear();
    navigation.reset({
      index: 0,
      routes: [{ name: 'Login' }],
    });
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
    card: {
      backgroundColor: isDarkMode ? '#1E293B' : '#FFF',
      borderColor: isDarkMode ? '#334155' : '#F1F5F9',
    },
    text: { color: isDarkMode ? '#F8FAFC' : Colors.textHeader },
    subText: { color: isDarkMode ? '#94A3B8' : Colors.textSub },
    divider: { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' },
    optionIconBox: { backgroundColor: isDarkMode ? '#334155' : '#EFF6FF' },
  };

  return (
    <SafeAreaView style={[styles.container, themeStyles.container]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#0F172A' : '#F8FAFC'}
      />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={[styles.headerTitle, themeStyles.text]}>
            {t.profile}
          </Text>
        </View>

        <TouchableOpacity
          style={[styles.userCard, themeStyles.card]}
          onPress={() => Alert.alert(t.accountInfo, `${user.name}\n${user.email}`)}>
          <View style={styles.avatarContainer}>
            <Image
              source={{ uri: (user as any).avatar }}
              style={styles.avatar}
            />
          </View>
          <View style={styles.userInfo}>
            <Text style={[styles.userName, themeStyles.text]}>{user.name}</Text>
            <Text style={[styles.userEmail, themeStyles.subText]}>
              {user.email}
            </Text>
          </View>
          <ChevronRight
            size={20}
            color={isDarkMode ? '#94A3B8' : Colors.textSub}
          />
        </TouchableOpacity>

        <View style={[styles.section, themeStyles.card]}>
          <ProfileOption
            icon={Moon}
            label={t.darkMode}
            showSwitch
            switchValue={isDarkMode}
            onSwitchChange={toggleDarkMode}
            isDarkMode={isDarkMode}
          />
          <View style={[styles.divider, themeStyles.divider]} />
          <ProfileOption
            icon={Globe}
            label={t.language}
            value={
              language === 'en' ? 'English' :
                language === 'ta' ? 'தமிழ்' :
                  language === 'hi' ? 'हिन्दी' :
                    language === 'te' ? 'తెలుగు' :
                      language === 'ml' ? 'മലയാളம்' :
                        language === 'kn' ? 'ಕನ್ನಡ' :
                          language === 'es' ? 'Español' :
                            language === 'fr' ? 'Français' :
                              language === 'ar' ? 'العربية' : '中文'
            }
            onPress={openLanguageModal}
            isDarkMode={isDarkMode}
          />
        </View>

        <View style={[styles.section, themeStyles.card]}>
          <ProfileOption
            icon={Shield}
            label={t.settings}
            onPress={() => navigation.navigate('Settings')}
            isDarkMode={isDarkMode}
          />
          <View style={[styles.divider, themeStyles.divider]} />
          <ProfileOption
            icon={HelpCircle}
            label={t.helpSupport}
            onPress={() => Alert.alert(t.helpSupport, "Contact us at support@medscan.ai for 24/7 medical drug verification assistance.")}
            isDarkMode={isDarkMode}
          />
          <View style={[styles.divider, themeStyles.divider]} />
          <ProfileOption
            icon={Info}
            label={t.about}
            onPress={() => Alert.alert(t.about, "MedScan-AI v1.0.2\nAdvanced Forensic AI for Medicine Authentication.")}
            isDarkMode={isDarkMode}
          />
        </View>

        <TouchableOpacity
          style={[
            styles.logoutBtn,
            themeStyles.card,
            { borderColor: isDarkMode ? '#7F1D1D' : '#FEE2E2' },
          ]}
          onPress={handleLogout}>
          <LogOut size={20} color={Colors.error} />
          <Text style={[styles.logoutText, { color: Colors.error }]}>
            {t.logout}
          </Text>
        </TouchableOpacity>

        <View style={[styles.versionContainer]}>
          <Text style={[styles.versionText, themeStyles.subText]}>
            Version 1.0.2
          </Text>
        </View>
      </ScrollView>

      {/* Language Selection Modal */}
      <Modal
        visible={showLangModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowLangModal(false)}>
        <View style={styles.modalOverlay}>
          <View
            style={[
              styles.modalContent,
              isDarkMode && { backgroundColor: '#1E293B' },
            ]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, isDarkMode && { color: '#F8FAFC' }]}>
                Select Language
              </Text>
              <TouchableOpacity onPress={() => setShowLangModal(false)}>
                <X size={24} color={isDarkMode ? '#F8FAFC' : Colors.textHeader} />
              </TouchableOpacity>
            </View>

            <ScrollView
              showsVerticalScrollIndicator={false}
              style={{ maxHeight: 400 }}>
              {[
                { id: 'en', label: 'English', sub: 'English' },
                { id: 'ta', label: 'தமிழ்', sub: 'Tamil' },
                { id: 'hi', label: 'हिन्दी', sub: 'Hindi' },
                { id: 'te', label: 'తెలుగు', sub: 'Telugu' },
                { id: 'ml', label: 'മലയാളം', sub: 'Malayalam' },
                { id: 'kn', label: 'ಕನ್ನಡ', sub: 'Kannada' },
                { id: 'es', label: 'Español', sub: 'Spanish' },
                { id: 'fr', label: 'Français', sub: 'French' },
                { id: 'ar', label: 'العربية', sub: 'Arabic' },
                { id: 'zh', label: '中文', sub: 'Chinese' },
              ].map(lang => (
                <TouchableOpacity
                  key={lang.id}
                  style={[
                    styles.langOption,
                    language === lang.id && {
                      backgroundColor: isDarkMode ? '#334155' : '#F1F5F9',
                      borderColor: Colors.primary,
                    },
                  ]}
                  onPress={() => selectLanguage(lang.id as Language)}>
                  <View>
                    <Text
                      style={[
                        styles.langLabel,
                        isDarkMode && { color: '#F8FAFC' },
                        language === lang.id && { color: Colors.primary },
                      ]}>
                      {lang.label}
                    </Text>
                    <Text style={styles.langSub}>{lang.sub}</Text>
                  </View>
                  {language === lang.id && (
                    <Check size={20} color={Colors.primary} />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>

      <View
        style={[
          styles.bottomTab,
          themeStyles.card,
          { borderTopColor: isDarkMode ? '#334155' : '#F1F5F9' },
        ]}>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => navigation.navigate('Home')}>
          <ShieldCheck
            size={24}
            color={isDarkMode ? '#94A3B8' : Colors.textSub}
          />
          <Text style={[styles.tabText, themeStyles.subText]}>{t.home}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={pickImageAndNavigate}>
          <ImageIcon size={24} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
          <Text style={[styles.tabText, themeStyles.subText]}>{t.upload}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => navigation.navigate('History')}>
          <HistoryIcon
            size={24}
            color={isDarkMode ? '#94A3B8' : Colors.textSub}
          />
          <Text style={[styles.tabText, themeStyles.subText]}>{t.history}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tabItem}>
          <View style={styles.activeTabCircle}>
            <UserIcon size={24} color={Colors.primary} />
          </View>
          <Text style={[styles.tabText, { color: Colors.primary }]}>
            {t.profile}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  scrollContent: { padding: 24, paddingBottom: 120 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
  },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: Colors.textHeader },
  bellBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },

  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 24,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#F1F5F9',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
  },
  avatarContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: Colors.primary,
  },
  avatar: { width: '100%', height: '100%' },
  userInfo: { flex: 1, marginLeft: 15 },
  userName: { fontSize: 18, fontWeight: 'bold', color: Colors.textHeader },
  userEmail: { fontSize: 12, color: Colors.textSub, marginTop: 2 },

  section: {
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 8,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  optionRow: { flexDirection: 'row', alignItems: 'center', padding: 12 },
  optionIconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  optionLabel: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: Colors.textHeader,
  },
  optionValue: { fontSize: 14, color: Colors.textSub, marginRight: 10 },
  divider: { height: 1, backgroundColor: '#F1F5F9', marginHorizontal: 12 },

  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 16,
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#FEE2E2',
    gap: 10,
  },
  logoutText: { fontSize: 16, fontWeight: 'bold', color: Colors.error },

  versionContainer: { alignItems: 'center', marginTop: 30 },
  versionText: { fontSize: 12, color: Colors.textSub },

  bottomTab: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 80,
    backgroundColor: '#FFF',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingBottom: 15,
  },
  tabItem: { alignItems: 'center' },
  tabText: { fontSize: 10, marginTop: 4, fontWeight: '600' },
  activeTabCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.textHeader,
  },
  langOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'transparent',
    marginBottom: 10,
  },
  langLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textHeader,
  },
  langSub: {
    fontSize: 12,
    color: Colors.textSub,
    marginTop: 2,
  },
});

export default ProfileScreen;
