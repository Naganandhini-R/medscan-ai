import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  FlatList,
  StatusBar,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  ChevronRight,
  ShieldCheck,
  AlertCircle,
  Clock,
  RefreshCw,
  History as HistoryIcon,
} from 'lucide-react-native';
import { Colors } from '../theme/Colors';
import { getRecentScans, ScanResult } from '../services/api.service';
import { useFocusEffect } from '@react-navigation/native';
import { translations, Language } from '../utils/translations';

// Removed old filters constant

const HistoryItem = ({
  item,
  onPress,
  isDarkMode,
  t,
}: {
  item: ScanResult;
  onPress: () => void;
  isDarkMode: boolean;
  t: any;
}) => {
  const isGenuine = item.status === 'GENUINE';
  const isSuspicious = item.status === 'SUSPICIOUS';
  const color = isGenuine
    ? Colors.success
    : isSuspicious
      ? Colors.warning
      : Colors.error;
  const bgColor = isGenuine
    ? isDarkMode
      ? '#064E3B'
      : '#ECFDF5'
    : isSuspicious
      ? isDarkMode
        ? '#451A03'
        : '#FFFBEB'
      : isDarkMode
        ? '#450A0A'
        : '#FEF2F2';
  const Icon = isGenuine ? ShieldCheck : isSuspicious ? Clock : AlertCircle;

  const statusLabel =
    item.status === 'GENUINE'
      ? t.genuine
      : item.status === 'SUSPICIOUS'
        ? t.suspicious
        : t.fake;

  return (
    <TouchableOpacity
      style={[
        styles.historyCard,
        {
          backgroundColor: isDarkMode ? '#1E293B' : '#FFF',
          borderColor: isDarkMode ? '#334155' : '#F1F5F9',
        },
      ]}
      onPress={onPress}>
      <View style={[styles.iconContainer, { backgroundColor: bgColor }]}>
        <Icon size={24} color={color} />
      </View>
      <View style={styles.itemInfo}>
        <View style={styles.nameRow}>
          <Text
            style={[
              styles.itemName,
              { color: isDarkMode ? '#F8FAFC' : Colors.textHeader },
            ]}
            numberOfLines={1}>
            {item.medicine_name || 'Generic Medicine'}
          </Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Text style={[styles.itemStatus, { color }]}>{statusLabel}</Text>
          <Text
            style={[
              styles.itemDate,
              { color: isDarkMode ? '#94A3B8' : Colors.textSub },
            ]}>
            {' '}
            • {new Date().toLocaleDateString()}
          </Text>
        </View>
      </View>
      <ChevronRight size={20} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
    </TouchableOpacity>
  );
};

const HistoryScreen = ({ navigation }: any) => {
  const [activeFilter, setActiveFilter] = useState('All');
  const [history, setHistory] = useState<ScanResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<Language>('en');

  const t = translations[language];

  const filters = [
    {
      id: 'All',
      label: language === 'en' ? 'All' : language === 'ta' ? 'அனைத்தும்' : 'सब',
    },
    { id: 'GENUINE', label: t.genuine },
    { id: 'FAKE', label: t.fake },
    { id: 'SUSPICIOUS', label: t.suspicious },
  ];

  useFocusEffect(
    useCallback(() => {
      fetchHistory();
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

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const userJson = await AsyncStorage.getItem('user');
      let userId = undefined;
      if (userJson) {
        userId = JSON.parse(userJson).id;
      }
      const data = await getRecentScans(50, userId);
      setHistory(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredData = history.filter(
    item => activeFilter === 'All' || item.status === activeFilter,
  );

  return (
    <SafeAreaView
      style={[
        styles.container,
        { backgroundColor: isDarkMode ? '#0F172A' : '#F8FAFC' },
      ]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#0F172A' : '#F8FAFC'}
      />
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={[
            styles.backBtn,
            {
              backgroundColor: isDarkMode ? '#1E293B' : '#FFF',
              borderColor: isDarkMode ? '#334155' : '#F1F5F9',
            },
          ]}>
          <ChevronRight
            size={24}
            color={isDarkMode ? '#F8FAFC' : Colors.textHeader}
            style={{ transform: [{ rotate: '180deg' }] }}
          />
        </TouchableOpacity>
        <Text
          style={[
            styles.headerTitle,
            { color: isDarkMode ? '#F8FAFC' : Colors.textHeader },
          ]}>
          {t.history}
        </Text>
        <TouchableOpacity style={styles.menuBtn} onPress={fetchHistory}>
          <RefreshCw size={24} color={Colors.primary} />
        </TouchableOpacity>
      </View>

      <View style={styles.filterContainer}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterScroll}>
          {filters.map(filter => (
            <TouchableOpacity
              key={filter.id}
              onPress={() => setActiveFilter(filter.id)}
              style={[
                styles.filterBtn,
                {
                  backgroundColor: isDarkMode ? '#1E293B' : '#FFF',
                  borderColor: isDarkMode ? '#334155' : '#F1F5F9',
                },
                activeFilter === filter.id && {
                  backgroundColor: Colors.primary,
                  borderColor: Colors.primary,
                },
              ]}>
              <Text
                style={[
                  styles.filterText,
                  { color: isDarkMode ? '#94A3B8' : Colors.textSub },
                  activeFilter === filter.id && styles.activeFilterText,
                ]}>
                {filter.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <FlatList
        data={filteredData}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <HistoryItem
            item={item}
            onPress={() => navigation.navigate('Result', { scanId: item.id })}
            isDarkMode={isDarkMode}
            t={t}
          />
        )}
        onRefresh={fetchHistory}
        refreshing={loading}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <HistoryIcon size={64} color="#E2E8F0" />
            <Text style={styles.emptyText}>
              No history found for this filter
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
  menuBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },

  filterContainer: { marginVertical: 10 },
  filterScroll: { paddingHorizontal: 20, gap: 10 },
  filterBtn: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  activeFilterBtn: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  filterText: { fontSize: 14, color: Colors.textSub, fontWeight: '600' },
  activeFilterText: { color: '#FFF' },

  listContent: { padding: 20, gap: 15, paddingBottom: 100 },
  historyCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#F1F5F9',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 5,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  itemInfo: { flex: 1, marginLeft: 15 },
  nameRow: { flexDirection: 'row', alignItems: 'center' },
  itemName: { fontSize: 16, fontWeight: 'bold', color: Colors.textHeader },
  itemStatus: { fontSize: 14, fontWeight: '600' },
  itemDate: { fontSize: 12, color: Colors.textSub, marginTop: 4 },

  emptyContainer: { alignItems: 'center', marginTop: 100 },
  emptyText: { marginTop: 20, fontSize: 16, color: Colors.textSub },
});

export default HistoryScreen;
