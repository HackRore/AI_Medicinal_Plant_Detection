// Mobile api configuration
// Change this to your actual production URL when deploying
const PROD_API_URL = 'https://api.yourmedicinalplantapp.com';

// Local development APIs
// 10.0.2.2 is special alias for localhost in Android Emulator
// localhost works for iOS Simulator
const DEV_API_URL_ANDROID = 'http://10.0.2.2:8000';
const DEV_API_URL_IOS = 'http://localhost:8000';

// Set this to true before building for production
const IS_PRODUCTION = false;

import { Platform } from 'react-native';

const BASE_URL = IS_PRODUCTION
    ? PROD_API_URL
    : (Platform.OS === 'android' ? DEV_API_URL_ANDROID : DEV_API_URL_IOS);

export const API_URL = `${BASE_URL}/api/v1/predict/`;

export const CONFIG = {
    IS_PRODUCTION,
    BASE_URL
};
