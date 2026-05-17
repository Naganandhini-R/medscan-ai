import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    TouchableOpacity,
    Switch,
    StatusBar,
    Alert,
} from 'react-native';
import {
    ArrowLeft,
    User,
    Bell,
    Lock,
    Eye,
    Trash2,
    FileText,
    HelpCircle,
    ChevronRight,
} from 'lucide-react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from '../theme/Colors';
import { translations, Language } from '../utils/translations';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Settings'>;

const SettingRow = ({ icon: Icon, label, value, onPress, showSwitch, switchValue, onSwitchChange, isDarkMode }: any) => (
    <TouchableOpacity
        style={[styles.row, isDarkMode && styles.rowDark]}
        onPress={onPress}
        disabled={showSwitch}
    >
        <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
            <Icon size={20} color={isDarkMode ? '#F8FAFC' : Colors.textHeader} />
        </View>
        <View style={styles.rowContent}>
            <Text style={[styles.label, isDarkMode && { color: '#F8FAFC' }]}>{label}</Text>
            {value && <Text style={styles.value}>{value}</Text>}
        </View>
        {showSwitch ? (
            <Switch
                value={switchValue}
                onValueChange={onSwitchChange}
                trackColor={{ false: '#E2E8F0', true: Colors.primary }}
                thumbColor="#FFF"
            />
        ) : (
            <ChevronRight size={18} color={isDarkMode ? '#94A3B8' : '#CBD5E1'} />
        )}
    </TouchableOpacity>
);

export default function SettingsScreen({ navigation }: Props) {
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [language, setLanguage] = useState<Language>('en');
    const [notifications, setNotifications] = useState(true);
    const [securityAlerts, setSecurityAlerts] = useState(true);
    const [biometrics, setBiometrics] = useState(false);

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const mode = await AsyncStorage.getItem('darkMode');
            const lang = await AsyncStorage.getItem('language');
            const notifs = await AsyncStorage.getItem('notifications');
            const secAlerts = await AsyncStorage.getItem('securityAlerts');

            if (mode !== null) setIsDarkMode(JSON.parse(mode));
            if (lang !== null) setLanguage(lang as Language);
            if (notifs !== null) setNotifications(JSON.parse(notifs));
            if (secAlerts !== null) setSecurityAlerts(JSON.parse(secAlerts));
        } catch (e) {
            console.error('Failed to load settings', e);
        }
    };

    const toggleDarkMode = async (val: boolean) => {
        setIsDarkMode(val);
        await AsyncStorage.setItem('darkMode', JSON.stringify(val));
    };

    const t = translations[language];

    const handleClearHistory = () => {
        Alert.alert(
            "Clear History",
            "Are you sure you want to delete all scan history? This action cannot be undone.",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Delete All",
                    style: "destructive",
                    onPress: async () => {
                        await AsyncStorage.removeItem('recentScans');
                        Alert.alert("Success", "Scan history cleared successfully.");
                    }
                }
            ]
        );
    };

    return (
        <SafeAreaView style={[styles.container, isDarkMode && styles.containerDark]}>
            <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <ArrowLeft size={24} color={isDarkMode ? '#F8FAFC' : Colors.textHeader} />
                </TouchableOpacity>
                <Text style={[styles.headerTitle, isDarkMode && { color: '#F8FAFC' }]}>{t.settings}</Text>
                <View style={{ width: 44 }} />
            </View>

            <ScrollView contentContainerStyle={styles.content}>
                <Text style={styles.sectionTitle}>Account</Text>
                <View style={[styles.section, isDarkMode && styles.sectionDark]}>
                    <SettingRow
                        icon={User}
                        label="Edit Profile"
                        onPress={() => navigation.navigate('EditProfile')}
                        isDarkMode={isDarkMode}
                    />
                    <View style={[styles.divider, isDarkMode && styles.dividerDark]} />
                    <SettingRow
                        icon={Lock}
                        label="Change Password"
                        onPress={() => navigation.navigate('ChangePassword')}
                        isDarkMode={isDarkMode}
                    />
                </View>

                <Text style={styles.sectionTitle}>Preferences</Text>
                <View style={[styles.section, isDarkMode && styles.sectionDark]}>
                    <SettingRow
                        icon={Eye}
                        label="Dark Mode"
                        showSwitch
                        switchValue={isDarkMode}
                        onSwitchChange={toggleDarkMode}
                        isDarkMode={isDarkMode}
                    />
                </View>

                <Text style={styles.sectionTitle}>Notifications</Text>
                <View style={[styles.section, isDarkMode && styles.sectionDark]}>
                    <SettingRow
                        icon={Bell}
                        label="Push Notifications"
                        showSwitch
                        switchValue={notifications}
                        onSwitchChange={async (val: boolean) => {
                            setNotifications(val);
                            await AsyncStorage.setItem('notifications', JSON.stringify(val));
                        }}
                        isDarkMode={isDarkMode}
                    />
                    <View style={[styles.divider, isDarkMode && styles.dividerDark]} />
                    <SettingRow
                        icon={Eye}
                        label="Security Alerts"
                        showSwitch
                        switchValue={securityAlerts}
                        onSwitchChange={async (val: boolean) => {
                            setSecurityAlerts(val);
                            await AsyncStorage.setItem('securityAlerts', JSON.stringify(val));
                            Alert.alert("Security Alerts", val ? "Forensic security notifications enabled." : "Security notifications disabled.");
                        }}
                        isDarkMode={isDarkMode}
                    />
                </View>

                <Text style={styles.sectionTitle}>Privacy & Security</Text>
                <View style={[styles.section, isDarkMode && styles.sectionDark]}>
                    <SettingRow
                        icon={Trash2}
                        label="Clear Scan History"
                        onPress={handleClearHistory}
                        isDarkMode={isDarkMode}
                    />
                </View>

                <Text style={styles.sectionTitle}>Support</Text>
                <View style={[styles.section, isDarkMode && styles.sectionDark]}>
                    <SettingRow
                        icon={HelpCircle}
                        label="FAQ"
                        onPress={() => Alert.alert(
                            "Frequently Asked Questions",
                            "Q: How accurate is the AI scan?\nA: MedScan-AI uses a forensic vision engine with 99.2% accuracy in detecting packaging anomalies.\n\nQ: Does it work without internet?\nA: Basic package scanning works offline, but blockchain verification requires a data connection.\n\nQ: What if a medicine is suspicious?\nA: Immediately use the 'Report Issue' feature to alert local authorities and the manufacturer."
                        )}
                        isDarkMode={isDarkMode}
                    />
                    <View style={[styles.divider, isDarkMode && styles.dividerDark]} />
                    <SettingRow
                        icon={FileText}
                        label="Privacy Policy"
                        onPress={() => Alert.alert(
                            "Privacy Policy",
                            "1. Data Collection: We collect only necessary medical scan data for authentication.\n\n2. Security: All your data is encrypted using forensic AI standards and blockchain logs.\n\n3. Third Parties: We never sell your medical or personal information to third-party advertisers.\n\n4. Control: You can delete your account and all associated data at any time from settings."
                        )}
                        isDarkMode={isDarkMode}
                    />
                </View>

                <TouchableOpacity
                    style={styles.deleteBtn}
                    onPress={() => Alert.alert("Delete Account", "This will permanently remove your data. Confirm?", [{ text: 'Cancel' }, { text: 'Delete', style: 'destructive' }])}
                >
                    <Trash2 size={20} color={Colors.error} />
                    <Text style={styles.deleteText}>Delete Account</Text>
                </TouchableOpacity>

                <View style={styles.footer}>
                    <Text style={styles.version}>MedScan-AI Version 1.0.2</Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F8FAFC' },
    containerDark: { backgroundColor: '#0F172A' },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 20,
        paddingVertical: 15,
    },
    backBtn: {
        width: 44,
        height: 44,
        borderRadius: 22,
        justifyContent: 'center',
        alignItems: 'center',
    },
    headerTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
    content: { padding: 20 },
    sectionTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#64748B',
        marginBottom: 10,
        marginTop: 20,
        marginLeft: 5,
        textTransform: 'uppercase',
    },
    section: {
        backgroundColor: '#FFF',
        borderRadius: 20,
        overflow: 'hidden',
        borderWidth: 1,
        borderColor: '#F1F5F9',
    },
    sectionDark: {
        backgroundColor: '#1E293B',
        borderColor: '#334155',
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 15,
    },
    rowDark: {
        backgroundColor: '#1E293B',
    },
    iconBox: {
        width: 40,
        height: 40,
        borderRadius: 12,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 15,
    },
    rowContent: { flex: 1 },
    label: { fontSize: 16, color: Colors.textHeader, fontWeight: '500' },
    value: { fontSize: 14, color: '#64748B', marginTop: 2 },
    divider: { height: 1, backgroundColor: '#F1F5F9', marginLeft: 70 },
    dividerDark: { backgroundColor: '#334155' },
    deleteBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 40,
        padding: 15,
        borderRadius: 15,
        backgroundColor: '#FEF2F2',
        gap: 10,
    },
    deleteText: { color: Colors.error, fontWeight: 'bold', fontSize: 16 },
    footer: { marginTop: 40, alignItems: 'center', paddingBottom: 20 },
    version: { color: '#94A3B8', fontSize: 12 },
});
