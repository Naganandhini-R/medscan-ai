import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    TouchableOpacity,
    TextInput,
    StatusBar,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { ArrowLeft, Lock, Eye, EyeOff, ShieldCheck } from 'lucide-react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from '../theme/Colors';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'ChangePassword'>;

export default function ChangePasswordScreen({ navigation }: Props) {
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showOldPass, setShowOldPass] = useState(false);
    const [showNewPass, setShowNewPass] = useState(false);
    const [showConfirmPass, setShowConfirmPass] = useState(false);

    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    useEffect(() => {
        loadTheme();
    }, []);

    const loadTheme = async () => {
        const mode = await AsyncStorage.getItem('darkMode');
        if (mode) setIsDarkMode(JSON.parse(mode));
    };

    const handleUpdate = async () => {
        if (!oldPassword || !newPassword || !confirmPassword) {
            Alert.alert("Error", "Please fill in all password fields.");
            return;
        }

        if (newPassword.length < 6) {
            Alert.alert("Error", "New password must be at least 6 characters long.");
            return;
        }

        if (newPassword !== confirmPassword) {
            Alert.alert("Error", "New passwords do not match.");
            return;
        }

        setLoading(true);
        // Simulate API call
        setTimeout(() => {
            setLoading(false);
            Alert.alert(
                "Success",
                "Your password has been securely updated.",
                [{ text: "OK", onPress: () => navigation.goBack() }]
            );
        }, 1500);
    };

    const PasswordInput = ({ label, value, onChange, show, setShow, placeholder }: any) => (
        <View style={styles.inputGroup}>
            <Text style={styles.label}>{label}</Text>
            <View style={[styles.inputWrapper, isDarkMode && styles.inputWrapperDark]}>
                <Lock size={18} color="#94A3B8" style={styles.inputIcon} />
                <TextInput
                    style={[styles.input, isDarkMode && { color: '#F8FAFC' }]}
                    value={value}
                    onChangeText={onChange}
                    secureTextEntry={!show}
                    placeholder={placeholder}
                    placeholderTextColor="#94A3B8"
                />
                <TouchableOpacity onPress={() => setShow(!show)} style={styles.eyeBtn}>
                    {show ? <EyeOff size={18} color="#94A3B8" /> : <Eye size={18} color="#94A3B8" />}
                </TouchableOpacity>
            </View>
        </View>
    );

    return (
        <SafeAreaView style={[styles.container, isDarkMode && styles.containerDark]}>
            <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />

            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <ArrowLeft size={24} color={isDarkMode ? '#F8FAFC' : Colors.textHeader} />
                </TouchableOpacity>
                <Text style={[styles.headerTitle, isDarkMode && { color: '#F8FAFC' }]}>Change Password</Text>
                <View style={{ width: 44 }} />
            </View>

            <ScrollView contentContainerStyle={styles.content}>
                <View style={styles.infoSection}>
                    <View style={[styles.shieldBox, { backgroundColor: isDarkMode ? 'rgba(34, 197, 94, 0.1)' : '#F0FDF4' }]}>
                        <ShieldCheck size={40} color={Colors.primary} />
                    </View>
                    <Text style={[styles.infoTitle, isDarkMode && { color: '#F8FAFC' }]}>Secure Update</Text>
                    <Text style={styles.infoText}>
                        Ensure your password is strong to protect your sensitive medical data and history.
                    </Text>
                </View>

                <View style={styles.form}>
                    <PasswordInput
                        label="Current Password"
                        value={oldPassword}
                        onChange={setOldPassword}
                        show={showOldPass}
                        setShow={setShowOldPass}
                        placeholder="Min 6 characters"
                    />

                    <PasswordInput
                        label="New Password"
                        value={newPassword}
                        onChange={setNewPassword}
                        show={showNewPass}
                        setShow={setShowNewPass}
                        placeholder="Create strong password"
                    />

                    <PasswordInput
                        label="Confirm New Password"
                        value={confirmPassword}
                        onChange={setConfirmPassword}
                        show={showConfirmPass}
                        setShow={setShowConfirmPass}
                        placeholder="Repeat new password"
                    />
                </View>

                <TouchableOpacity
                    style={[styles.actionBtn, loading && { opacity: 0.7 }]}
                    onPress={handleUpdate}
                    disabled={loading}
                >
                    {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.actionBtnText}>Update Password</Text>}
                </TouchableOpacity>

                <Text style={styles.footerNote}>
                    If you forgot your password, please use the logout option and reset from the login screen.
                </Text>
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
    backBtn: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
    headerTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
    content: { padding: 20 },
    infoSection: { alignItems: 'center', marginBottom: 40 },
    shieldBox: {
        width: 80,
        height: 80,
        borderRadius: 24,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 15,
    },
    infoTitle: { fontSize: 22, fontWeight: 'bold', color: Colors.textHeader, marginBottom: 8 },
    infoText: { fontSize: 14, color: '#64748B', textAlign: 'center', paddingHorizontal: 20, lineHeight: 20 },
    form: { gap: 20 },
    inputGroup: { gap: 8 },
    label: { fontSize: 14, fontWeight: 'bold', color: '#64748B', marginLeft: 4 },
    inputWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFF',
        borderRadius: 15,
        borderWidth: 1,
        borderColor: '#F1F5F9',
        paddingHorizontal: 15,
        height: 56,
    },
    inputWrapperDark: { backgroundColor: '#1E293B', borderColor: '#334155' },
    inputIcon: { marginRight: 12 },
    input: { flex: 1, fontSize: 16, color: Colors.textHeader },
    eyeBtn: { padding: 8 },
    actionBtn: {
        backgroundColor: Colors.primary,
        height: 56,
        borderRadius: 15,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 40,
        elevation: 4,
    },
    actionBtnText: { color: '#FFF', fontSize: 18, fontWeight: 'bold' },
    footerNote: { fontSize: 12, color: '#94A3B8', textAlign: 'center', marginTop: 30, paddingHorizontal: 40 },
});
