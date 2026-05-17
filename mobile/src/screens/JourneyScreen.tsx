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
  Box,
  Factory,
  Truck,
  Store,
  Database,
  ShieldCheck,
  MapPin,
  Calendar,
} from 'lucide-react-native';
import StepIndicator from 'react-native-step-indicator';
import {Colors} from '../theme/Colors';

const stepIndicatorStyles = {
  stepIndicatorSize: 34,
  currentStepIndicatorSize: 42,
  separatorStrokeWidth: 3,
  currentStepStrokeWidth: 4,
  stepStrokeCurrentColor: Colors.primary,
  stepStrokeWidth: 2,
  stepStrokeFinishedColor: Colors.primary,
  stepStrokeUnFinishedColor: '#cbd5e1',
  separatorFinishedColor: Colors.primary,
  separatorUnFinishedColor: '#e2e8f0',
  stepIndicatorFinishedColor: Colors.primary,
  stepIndicatorUnFinishedColor: '#ffffff',
  stepIndicatorCurrentColor: '#ffffff',
  stepIndicatorLabelFontSize: 0,
  currentStepIndicatorLabelFontSize: 0,
  stepIndicatorLabelCurrentColor: 'transparent',
  stepIndicatorLabelFinishedColor: 'transparent',
  stepIndicatorLabelUnFinishedColor: 'transparent',
  labelColor: '#64748b',
  labelSize: 13,
  currentStepLabelColor: Colors.primary,
};

export default function JourneyScreen({route, navigation}: any) {
  const {batchNo, journey: rawJourney} = route.params;

  const getIcon = (type: string) => {
    switch (type) {
      case 'factory':
        return Factory;
      case 'warehouse':
        return Truck;
      case 'store':
        return Store;
      default:
        return Database;
    }
  };

  const journeySteps = Array.isArray(rawJourney)
    ? rawJourney.map((s: any) => ({
        ...s,
        Icon: getIcon(s.type || ''),
        title: s.title || s.status || 'Update',
        date: s.date || s.timestamp || '',
      }))
    : [];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backBtn}>
          <ArrowLeft size={22} color={Colors.textHeader} />
        </TouchableOpacity>
        <View style={styles.titleContainer}>
          <Text style={styles.title}>Supply Chain Tracking</Text>
          <Text style={styles.subtitle}>Batch Verification: {batchNo}</Text>
        </View>
        <ShieldCheck size={24} color={Colors.success} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}>
        {journeySteps.length > 0 ? (
          <View style={styles.journeyBody}>
            <View style={styles.indicatorContainer}>
              <StepIndicator
                customStyles={stepIndicatorStyles}
                currentPosition={journeySteps.length - 1}
                direction="vertical"
                stepCount={journeySteps.length}
                renderStepIndicator={({stepStatus, position}) => {
                  const StepIcon = journeySteps[position].Icon;
                  return (
                    <StepIcon
                      size={stepStatus === 'current' ? 18 : 14}
                      color={
                        stepStatus === 'finished' ? '#FFF' : Colors.primary
                      }
                    />
                  );
                }}
              />
            </View>

            <View style={styles.detailsContainer}>
              {journeySteps.map((step: any, index: number) => (
                <View
                  key={index}
                  style={[
                    styles.stepCard,
                    index === journeySteps.length - 1 && styles.currentCard,
                  ]}>
                  <View style={styles.stepHeader}>
                    <View style={styles.stepInfo}>
                      <Text style={styles.stepTitle}>{step.title}</Text>
                      <View style={styles.locationRow}>
                        <MapPin size={12} color={Colors.textSub} />
                        <Text style={styles.stepLocation}>{step.location}</Text>
                      </View>
                    </View>
                    <View
                      style={[
                        styles.statusBadge,
                        {
                          backgroundColor:
                            index === journeySteps.length - 1
                              ? '#DCFCE7'
                              : '#F1F5F9',
                        },
                      ]}>
                      <Text
                        style={[
                          styles.statusText,
                          {
                            color:
                              index === journeySteps.length - 1
                                ? Colors.success
                                : Colors.textSub,
                          },
                        ]}>
                        {index === journeySteps.length - 1
                          ? 'Current'
                          : 'Verified'}
                      </Text>
                    </View>
                  </View>
                  <View style={styles.descBox}>
                    <Text style={styles.stepDesc}>{step.desc}</Text>
                  </View>
                  <View style={styles.cardFooter}>
                    <Calendar size={12} color={Colors.textSub} />
                    <Text style={styles.timestamp}>{step.date}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        ) : (
          <View style={styles.emptyContainer}>
            <Database size={64} color="#E2E8F0" />
            <Text style={styles.emptyText}>
              No supply chain tracking information available for this batch yet.
            </Text>
          </View>
        )}

        <View style={styles.blockchainInfo}>
          <ShieldCheck size={20} color={Colors.primary} />
          <View style={{flex: 1}}>
            <Text style={styles.blockchainTitle}>Blockchain Secured Data</Text>
            <Text style={styles.blockchainText}>
              Every step is cryptographically signed and stored on the Ethereum
              (Ganache) network.
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#FFFFFF'},
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  titleContainer: {flex: 1},
  title: {fontSize: 18, fontWeight: 'bold', color: Colors.textHeader},
  subtitle: {fontSize: 12, color: Colors.textSub, marginTop: 2},

  scrollContent: {paddingBottom: 50},
  journeyBody: {flexDirection: 'row', paddingHorizontal: 15, paddingTop: 20},
  indicatorContainer: {width: 40},
  detailsContainer: {flex: 1, paddingLeft: 10},

  stepCard: {
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#F1F5F9',
    shadowColor: '#64748b',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.08,
    shadowRadius: 10,
    elevation: 3,
  },
  currentCard: {
    borderColor: Colors.primary + '30',
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
  },
  stepHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  stepInfo: {flex: 1},
  stepTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginBottom: 4,
  },
  locationRow: {flexDirection: 'row', alignItems: 'center', gap: 4},
  stepLocation: {fontSize: 12, color: Colors.textSub},
  statusBadge: {paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12},
  statusText: {fontSize: 10, fontWeight: 'bold'},
  descBox: {marginBottom: 15, paddingVertical: 5},
  stepDesc: {fontSize: 13, color: Colors.textHeader, lineHeight: 20},
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    opacity: 0.7,
  },
  timestamp: {fontSize: 11, color: Colors.textSub, fontWeight: '500'},

  blockchainInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    margin: 20,
    padding: 20,
    backgroundColor: '#F8FAFC',
    borderRadius: 20,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: '#CBD5E1',
  },
  blockchainTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginBottom: 4,
  },
  blockchainText: {fontSize: 12, color: Colors.textSub, lineHeight: 18},
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 100,
    gap: 20,
  },
  emptyText: {
    textAlign: 'center',
    color: Colors.textSub,
    fontSize: 14,
    marginHorizontal: 40,
    lineHeight: 22,
  },
});
