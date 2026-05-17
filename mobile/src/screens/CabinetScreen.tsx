import React, { useState, useCallback } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TouchableOpacity,
  StatusBar,
  Image,
} from 'react-native';
import {
  Box,
  Search,
  Plus,
  ChevronRight,
  AlertCircle,
  Clock,
  ArrowLeft,
  LayoutGrid,
  List as ListIcon,
  Archive,
} from 'lucide-react-native';
import * as Progress from 'react-native-progress';
import { Colors } from '../theme/Colors';
import { translations, Language } from '../utils/translations';

// Initial data placeholder removed - loading from AsyncStorage

const CabinetItem = ({
  item,
  isDarkMode,
  t,
}: {
  item: any;
  isDarkMode: boolean;
  t: any;
}) => {
  const stockPercentage = item.stock / item.maxStock;
  const isLowStock = item.stock < 5;
  const isExpiringSoon = item.expiry.includes('2025');

  return (
    <TouchableOpacity
      style={[
        styles.itemCard,
        isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' },
      ]}>
      <View style={[styles.colorIndicator, { backgroundColor: item.color }]} />
      <View style={styles.itemMain}>
        <View style={styles.itemHeader}>
          <View>
            <Text style={[styles.itemName, isDarkMode && { color: '#F8FAFC' }]}>
              {item.name}
            </Text>
            <Text style={[styles.brandName, isDarkMode && { color: '#94A3B8' }]}>
              {item.brand}
            </Text>
          </View>
          <ChevronRight
            size={18}
            color={isDarkMode ? '#94A3B8' : Colors.textSub}
          />
        </View>

        <View style={styles.stockSection}>
          <View style={styles.stockLabelRow}>
            <Text style={[styles.stockLabel, isDarkMode && { color: '#94A3B8' }]}>
              {t.stockLevel || 'Stock Level'}
            </Text>
            <Text
              style={[
                styles.stockValue,
                isLowStock && { color: Colors.error },
                !isLowStock && isDarkMode && { color: Colors.primary },
              ]}>
              {item.stock}/{item.maxStock} {t.pills || 'Pills'}
            </Text>
          </View>
          <Progress.Bar
            progress={stockPercentage}
            width={null}
            height={6}
            color={isLowStock ? Colors.error : Colors.primary}
            unfilledColor={isDarkMode ? '#334155' : '#F1F5F9'}
            borderWidth={0}
          />
        </View>

        <View style={styles.badgesRow}>
          <View
            style={[
              styles.badge,
              { backgroundColor: isDarkMode ? '#334155' : '#F8FAFC' },
            ]}>
            <Clock size={12} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
            <Text style={[styles.badgeText, isDarkMode && { color: '#94A3B8' }]}>
              {t.exp || 'Exp'}: {item.expiry}
            </Text>
          </View>
          {isLowStock && (
            <View
              style={[
                styles.badge,
                { backgroundColor: isDarkMode ? '#450A0A' : '#FEF2F2' },
              ]}>
              <AlertCircle size={12} color={Colors.error} />
              <Text style={[styles.badgeText, { color: Colors.error }]}>
                {t.lowStock || 'Low Stock'}
              </Text>
            </View>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
};

export default function CabinetScreen({ navigation }: any) {
  const [cabinetItems, setCabinetItems] = useState<any[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<Language>('en');

  const t = translations[language];

  useFocusEffect(
    useCallback(() => {
      loadCabinet();
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

  const loadCabinet = async () => {
    try {
      const data = await AsyncStorage.getItem('cabinet');
      if (data) {
        setCabinetItems(JSON.parse(data));
      } else {
        setCabinetItems([]);
      }
    } catch (e) {
      console.error('Failed to load cabinet:', e);
    }
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <View
        style={[
          styles.emptyIconCircle,
          isDarkMode && { backgroundColor: '#1E293B' },
        ]}>
        <Archive size={40} color={isDarkMode ? '#475569' : '#CBD5E1'} />
      </View>
      <Text style={[styles.emptyTitle, isDarkMode && { color: '#F8FAFC' }]}>
        Your Cabinet is Empty
      </Text>
      <Text style={[styles.emptySubtitle, isDarkMode && { color: '#94A3B8' }]}>
        Scan a medicine and click "Add to Cabinet" to see it here.
      </Text>
      <TouchableOpacity
        style={styles.scanNowBtn}
        onPress={() => navigation.navigate('Scan')}>
        <Text style={styles.scanNowText}>Scan Now</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView
      style={[styles.container, isDarkMode && { backgroundColor: '#0F172A' }]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#0F172A' : '#F8FAFC'}
      />
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={[
            styles.backBtn,
            isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' },
          ]}>
          <ArrowLeft
            size={24}
            color={isDarkMode ? '#F8FAFC' : Colors.textHeader}
          />
        </TouchableOpacity>
        <Text style={[styles.title, isDarkMode && { color: '#F8FAFC' }]}>
          {t.myCabinet}
        </Text>
        <TouchableOpacity
          style={styles.addBtn}
          onPress={() => navigation.navigate('Scan')}>
          <Plus size={24} color="#FFF" />
        </TouchableOpacity>
      </View>

      <View
        style={[
          styles.searchBar,
          isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' },
        ]}>
        <Search
          size={20}
          color={isDarkMode ? '#94A3B8' : Colors.textSub}
          style={styles.searchIcon}
        />
        <Text
          style={[styles.searchPlaceholder, isDarkMode && { color: '#94A3B8' }]}>
          {t.searchCabinet || 'Search your cabinet...'}
        </Text>
      </View>

      <FlatList
        data={cabinetItems}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <CabinetItem item={item} isDarkMode={isDarkMode} t={t} />
        )}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmptyState}
        ListHeaderComponent={
          <View
            style={[
              styles.summaryCard,
              isDarkMode && {
                backgroundColor: '#1E293B',
                borderColor: '#334155',
              },
            ]}>
            <View style={styles.summaryItem}>
              <Text
                style={[styles.summaryNum, isDarkMode && { color: '#F8FAFC' }]}>
                {cabinetItems.length}
              </Text>
              <Text
                style={[styles.summaryLabel, isDarkMode && { color: '#94A3B8' }]}>
                {t.totalMeds || 'Total Meds'}
              </Text>
            </View>
            <View
              style={[
                styles.summaryDivider,
                isDarkMode && { backgroundColor: '#334155' },
              ]}
            />
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryNum, { color: Colors.error }]}>
                {cabinetItems.filter(i => i.stock < 5).length}
              </Text>
              <Text
                style={[styles.summaryLabel, isDarkMode && { color: '#94A3B8' }]}>
                {t.lowStock || 'Low Stock'}
              </Text>
            </View>
            <View
              style={[
                styles.summaryDivider,
                isDarkMode && { backgroundColor: '#334155' },
              ]}
            />
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryNum, { color: Colors.warning }]}>
                {cabinetItems.filter(i => i.expiry.includes('2025')).length}
              </Text>
              <Text
                style={[styles.summaryLabel, isDarkMode && { color: '#94A3B8' }]}>
                {t.expiringSoon || 'Expiring Soon'}
              </Text>
            </View>
          </View>
        }
      />
    </SafeAreaView>
  );
}

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
  title: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
  addBtn: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
  },

  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 20,
    paddingHorizontal: 15,
    height: 50,
    backgroundColor: '#FFF',
    borderRadius: 15,
    borderWidth: 1,
    borderColor: '#F1F5F9',
    marginBottom: 20,
  },
  searchIcon: { marginRight: 10 },
  searchPlaceholder: { flex: 1, color: Colors.textSub, fontSize: 14 },

  summaryCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 20,
    marginBottom: 25,
    borderWidth: 1,
    borderColor: '#F1F5F9',
    elevation: 2,
  },
  summaryItem: { flex: 1, alignItems: 'center' },
  summaryNum: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
  summaryLabel: { fontSize: 11, color: Colors.textSub, marginTop: 4 },
  summaryDivider: { width: 1, height: '100%', backgroundColor: '#F1F5F9' },

  listContent: { padding: 20, paddingBottom: 50 },
  itemCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 20,
    marginBottom: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#F1F5F9',
    elevation: 2,
  },
  colorIndicator: { width: 6 },
  itemMain: { flex: 1, padding: 16 },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  itemName: { fontSize: 18, fontWeight: 'bold', color: Colors.textHeader },
  brandName: { fontSize: 12, color: Colors.textSub, marginTop: 2 },

  stockSection: { marginBottom: 15 },
  stockLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  stockLabel: { fontSize: 12, color: Colors.textSub },
  stockValue: { fontSize: 12, fontWeight: 'bold', color: Colors.primary },

  badgesRow: { flexDirection: 'row', gap: 10 },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    gap: 5,
  },
  badgeText: { fontSize: 11, fontWeight: '600', color: Colors.textSub },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 40,
  },
  emptyIconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: Colors.textSub,
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 20,
  },
  scanNowBtn: {
    backgroundColor: Colors.primary,
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 12,
    elevation: 4,
  },
  scanNowText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
