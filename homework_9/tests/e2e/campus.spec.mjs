import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';
import {TEST_ADMIN_PASSWORD} from '../support/server.mjs';
async function login(page){await page.goto('/');await page.getByRole('button',{name:'登入校務平台 →'}).click();await expect(page.locator('#shell')).toBeVisible()}
async function adminLogin(page){await page.goto('/admin.html');await expect(page.locator('#adminLogin')).toBeVisible();await page.getByLabel('管理員密碼').fill(TEST_ADMIN_PASSWORD);await page.getByRole('button',{name:'登入管理後台',exact:true}).click();await expect(page.locator('#adminShell')).toBeVisible()}
test('E2E：錯誤密碼提示、成功登入與登出',async({page})=>{
 await page.goto('/');await page.getByLabel('密碼',{exact:true}).fill('wrong');await page.getByRole('button',{name:'登入校務平台 →'}).click();await expect(page.getByRole('status')).toHaveText('帳號或密碼錯誤');
 await page.getByLabel('密碼',{exact:true}).fill('student123');await page.getByRole('button',{name:'登入校務平台 →'}).click();await expect(page.locator('#shell')).toBeVisible();await page.getByRole('button',{name:'登出帳號 ↗'}).click();await expect(page.locator('#login')).toBeVisible();
});
test('E2E：搜尋加選、課表更新、重新整理保存與退選',async({page})=>{
 await login(page);await page.locator('nav').getByRole('button',{name:'選課系統'}).click();await page.getByRole('textbox',{name:'搜尋課程'}).fill('金門');const row=page.getByRole('row').filter({hasText:'GE201'});await row.getByRole('button',{name:'加選',exact:true}).click();await expect(page.getByRole('status')).toHaveText('加選成功');
 await page.locator('nav').getByRole('button',{name:'我的課表'}).click();await expect(page.locator('.schedule')).toContainText('金門文化與歷史');await page.reload();await expect(page.locator('#shell')).toBeVisible();await page.locator('nav').getByRole('button',{name:'我的課表'}).click();await expect(page.locator('.schedule')).toContainText('金門文化與歷史');
 await page.locator('nav').getByRole('button',{name:'選課系統'}).click();page.once('dialog',dialog=>dialog.accept());await page.getByRole('row').filter({hasText:'GE201'}).getByRole('button',{name:'退選',exact:true}).click();await expect(page.getByRole('status')).toHaveText('退選成功');
});
test('E2E：衝堂、額滿及 CSV 下載內容',async({page})=>{
 await login(page);await page.locator('nav').getByRole('button',{name:'選課系統'}).click();await page.getByRole('row').filter({hasText:'CS304'}).getByRole('button',{name:'加選',exact:true}).click();await expect(page.getByRole('status')).toHaveText('此課程與已選課程衝堂');await expect(page.getByRole('row').filter({hasText:'GE202'}).getByRole('button',{name:'已額滿'})).toBeDisabled();
 await page.locator('nav').getByRole('button',{name:'我的課表'}).click();const downloading=page.waitForEvent('download');await page.getByRole('button',{name:'匯出 CSV ↓'}).click();const download=await downloading;expect(download.suggestedFilename()).toBe('我的課表.csv');const csv=await readFile(await download.path(),'utf8');expect(csv).toContain('CS301');expect(csv).toContain('作業系統');expect(csv).not.toContain('CS304');
});
test('E2E：學生直接進入後台仍被阻擋',async({page})=>{await login(page);await page.goto('/admin.html');await expect(page.locator('#gateText')).toContainText('目前是學生帳號');await expect(page.locator('#adminShell')).toBeHidden()});
test('E2E：管理員發布與編輯公告，學生可見，最後清理',async({page,browser})=>{
 await adminLogin(page);await page.getByRole('button',{name:'公告管理',exact:false}).first().click();await page.getByRole('button',{name:'＋ 發布公告'}).click();await page.getByLabel('標題',{exact:true}).fill('E2E測試公告');await page.getByLabel('內容',{exact:true}).fill('瀏覽器建立的公告');await page.getByRole('button',{name:'儲存資料',exact:true}).click();await expect(page.locator('#editor')).not.toBeVisible();
 const row=page.getByRole('row').filter({hasText:'E2E測試公告'});await row.getByRole('button',{name:'編輯',exact:true}).click();await expect(page.locator('#editor')).toBeVisible();const bodyField=page.locator('#editor').getByLabel('內容',{exact:true});await expect(bodyField).toHaveValue('瀏覽器建立的公告');await bodyField.fill('E2E更新後內容');await page.getByRole('button',{name:'儲存資料',exact:true}).click();await expect(row).toContainText('E2E更新後內容');
 const context=await browser.newContext();const studentPage=await context.newPage();await studentPage.goto('http://127.0.0.1:8790/');await studentPage.getByRole('button',{name:'登入校務平台 →'}).click();await expect(studentPage.locator('#shell')).toBeVisible();await studentPage.locator('nav').getByRole('button',{name:'校園公告'}).click();await expect(studentPage.locator('#main')).toContainText('E2E更新後內容');await context.close();
 page.once('dialog',d=>d.accept());await row.getByRole('button',{name:'刪除',exact:true}).click();await expect(row).toHaveCount(0);
});
test('E2E：後台新增課程與修改成績',async({page})=>{
 await adminLogin(page);await page.locator('nav').getByRole('button',{name:'課程管理'}).click();await page.getByRole('button',{name:'＋ 新增課程'}).click();for(const [label,value] of [['課號','E2E101'],['課程名稱','E2E課程'],['教師','測試教師'],['教室','B101']])await page.getByLabel(label,{exact:true}).fill(value);await page.getByRole('button',{name:'儲存資料',exact:true}).click();await expect(page.getByRole('row').filter({hasText:'E2E101'})).toBeVisible();
 await page.locator('nav').getByRole('button',{name:'成績登錄'}).click();await page.getByRole('button',{name:'＋ 登錄成績'}).click();await page.getByLabel('課程名稱',{exact:true}).fill('E2E課程');await page.getByLabel('分數',{exact:true}).fill('92');await page.getByRole('button',{name:'儲存資料',exact:true}).click();const grade=page.getByRole('row').filter({hasText:'E2E課程'});await expect(grade).toContainText('92');await grade.getByRole('button',{name:'修改成績'}).click();await page.getByLabel('分數',{exact:true}).fill('96');await page.getByRole('button',{name:'儲存資料',exact:true}).click();await expect(grade).toContainText('96');await expect(grade).toHaveCount(1);
});
