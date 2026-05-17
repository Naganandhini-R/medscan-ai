export interface ScanResult {
    id: string;
    status: 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'GENUINE' | 'SUSPICIOUS' | 'COUNTERFEIT' | 'FAKE';
    score: number;
    blockchain_valid: boolean;
    medicine_name?: string;
    batch_id?: string;
    expiry?: string;
    manufacturer?: string;
    salts?: string;
    data?: any;
}


import { Platform, NativeModules } from 'react-native';

// 🌐 PRODUCTION-READY NETWORK CONFIGURATION
// For USB debugging: Run 'adb reverse tcp:8000 tcp:8000' and use 'localhost'
// For Wi-Fi: Use your current PC IP
const PC_IP = '192.168.50.94'; 

// Auto-detect environment
const getBaseUrl = () => {
    if (__DEV__) {
        // 1. DYNAMIC IP DETECTION (Best for Wi-Fi)
        // Detects the IP of the machine running the Metro bundler
        const scriptURL = NativeModules.SourceCode?.scriptURL || '';
        const packagerIP = scriptURL.split('://')[1]?.split(':')[0];
        
        if (packagerIP && packagerIP !== 'localhost' && packagerIP !== '127.0.0.1') {
            return `http://${packagerIP}:8000`;
        }

        // 2. Android Emulator uses 10.0.2.2 to access the host machine
        if (Platform.OS === 'android' && !PC_IP.includes('192.168')) {
            return 'http://10.0.2.2:8000';
        }
        
        // 3. If USB debugging with 'adb reverse tcp:8000 tcp:8000', use PC_IP (will be localhost or current IP)
        return `http://${PC_IP}:8000`;
    }
    return 'https://api.medscan.ai'; // Production URL placeholder
};

const BASE_URL = getBaseUrl();
export const API_URL = `${BASE_URL}/api/v1`;

console.log('[MedScan] Booting with API Endpoint:', API_URL);

/**
 * HEALTH CHECK: Verify backend connectivity
 */
export async function checkBackendHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${BASE_URL}/`, { method: 'GET' });
        return response.ok;
    } catch (e) {
        console.warn('❌ MedScan Backend Unreachable. Check IP:', PC_IP);
        return false;
    }
}


export async function uploadScan(images: { [key: string]: string | undefined }, metadata?: any): Promise<string> {
    const formData = new FormData();

    const formatUri = (path: string) => path.startsWith('file://') ? path : `file://${path}`;

    // Append images
    if (images.front) {
        formData.append('front', {
            uri: formatUri(images.front),
            type: 'image/jpeg',
            name: 'front.jpg',
        } as any);
    }

    if (images.back) {
        formData.append('back', {
            uri: formatUri(images.back),
            type: 'image/jpeg',
            name: 'back.jpg',
        } as any);
    }

    if (images.composition) {
        formData.append('strip', {
            uri: formatUri(images.composition),
            type: 'image/jpeg',
            name: 'strip.jpg',
        } as any);
    }

    if (metadata) {
        if (metadata.name) formData.append('medicine_name', metadata.name);
        if (metadata.batchId) formData.append('batch_id', metadata.batchId);
        if (metadata.expiryDate) formData.append('expiry', metadata.expiryDate);
        if (metadata.salts) formData.append('salts', JSON.stringify(metadata.salts));
        if (metadata.manufacturer) formData.append('manufacturer', metadata.manufacturer);
        if (metadata.userId) formData.append('user_id', metadata.userId);
    }

    try {
        const response = await fetch(`${API_URL}/scan/verify`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Upload failed: ${response.status}`);
        }

        const data = await response.json();
        console.log('Upload success, Scan ID:', data.scan_id);
        return data.scan_id;
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

export async function getResult(scanId: string): Promise<ScanResult> {
    const url = `${API_URL}/scan/result/${scanId}`;
    console.log('Fetching result from:', url);
    try {
        const response = await fetch(url);
        if (!response.ok) {
            console.error(`Fetch failed for ${url} with status ${response.status}`);
            throw new Error(`Fetch failed: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Get result error:', error);
        throw error;
    }
}


export async function getNearbyFakes(lat: number, lng: number): Promise<any[]> {
    try {
        const response = await fetch(`${API_URL}/admin/nearby-fakes?lat=${lat}&lng=${lng}`);
        if (!response.ok) {
            return [];
        }
        return await response.json();
    } catch (error) {
        console.error('Get nearby fakes error:', error);
        return [];
    }
}

// Auth functions
export async function login(email: string, password: string): Promise<any> {
    console.log(`[MedScan] Attempting login for ${email} at ${API_URL}`);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); // Increased to 20s for local network stability

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Login failed');
        }
        return await response.json();
    } catch (error: any) {
        console.error('[MedScan] Login error:', error);
        if (error.name === 'AbortError' || error.message.includes('fetch')) {
            throw new Error(`NETWORK ERROR: Ensure your phone is on the SAME Wi-Fi as your PC (${PC_IP}) and the backend is running.`);
        }
        throw error;
    }
}

export async function signup(full_name: string, email: string, password: string): Promise<any> {
    console.log(`[MedScan] Attempting signup for ${email} at ${API_URL}`);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); // 20s timeout

    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name, email, password }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Signup failed');
        }
        return await response.json();
    } catch (error: any) {
        console.error('[MedScan] Signup error:', error);
        if (error.name === 'AbortError') throw new Error('Connection timed out. Check your IP/Firewall.');
        throw error;
    }
}

export async function resetPassword(email: string, new_password: string): Promise<any> {
    const response = await fetch(`${API_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, new_password }),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Reset failed');
    }
    return await response.json();
}

export async function finishOnboarding(userId: string): Promise<any> {
    const response = await fetch(`${API_URL}/auth/finish-onboarding/${userId}`, {
        method: 'POST',
    });
    if (!response.ok) throw new Error('Onboarding finish failed');
    return await response.json();
}

export async function googleLogin(email: string, name: string): Promise<any> {
    const response = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            token: 'simulated_google_token_' + Date.now(),
            email,
            name
        }),
    });


    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Google login failed');
    }
    return await response.json();
}

export async function updateProfile(userId: string, full_name: string, email: string): Promise<any> {
    const response = await fetch(`${API_URL}/auth/update-profile/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name, email }),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Profile update failed');
    }
    return await response.json();
}

// Stats & History
export async function getStats(userId?: string): Promise<any> {
    try {
        const url = userId ? `${API_URL}/admin/stats?user_id=${userId}` : `${API_URL}/admin/stats`;
        const response = await fetch(url);
        if (!response.ok) return { total_scans: 0, fake_detected: 0, genuine: 0 };
        return await response.json();
    } catch (error) {
        console.error('Get stats error:', error);
        return { total_scans: 0, fake_detected: 0, genuine: 0 };
    }
}

export async function getRecentScans(limit: number = 5, userId?: string): Promise<ScanResult[]> {
    try {
        const url = userId
            ? `${API_URL}/admin/recent?limit=${limit}&user_id=${userId}`
            : `${API_URL}/admin/recent?limit=${limit}`;
        const response = await fetch(url);
        if (!response.ok) return [];
        return await response.json();
    } catch (error) {
        console.error('Get recent scans error:', error);
        return [];
    }
}
export async function submitReport(reportData: {
    scan_id?: string;
    medicine_name: string;
    batch_id: string;
    issue_type: string;
    location_details: string;
    description: string;
    lat?: number;
    lng?: number;
    manufacturer?: string;
}): Promise<any> {
    try {
        const response = await fetch(`${API_URL}/report/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reportData),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to submit report');
        }
        return await response.json();
    } catch (error) {
        console.error('Submit report error:', error);
        throw error;
    }
}

export async function scanSingleMedicine(imageUri: string): Promise<ScanResult> {
    const images = { front: imageUri };
    const scanId = await uploadScan(images);

    // Wait for result with improved polling frequency (Faster response)
    let attempts = 0;
    const maxAttempts = 15; // 15 * 800ms = ~12 seconds total timeout

    while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 800)); // Check every 800ms
        const result = await getResult(scanId);
        if (result.status !== 'PROCESSING') {
            return result;
        }
        attempts++;
    }

    return await getResult(scanId);
}
