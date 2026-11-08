import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests/e2e',fullyParallel:false,workers:1,retries:0,timeout:30000,
 reporter:[['list'],['html',{outputFolder:'playwright-report',open:'never'}]],
 use:{baseURL:'http://127.0.0.1:8790',headless:true,browserName:'chromium',viewport:{width:1440,height:1000},screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node tests/support/server.mjs',url:'http://127.0.0.1:8790',reuseExistingServer:false,timeout:30000}
});
