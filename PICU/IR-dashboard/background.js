// 백그라운드 스크립트
chrome.runtime.onInstalled.addListener(() => {
    console.log('AI Voice Summarizer 확장 프로그램이 설치되었습니다.');
});

// 메시지 처리 (향후 확장 가능)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'GET_STORAGE_DATA') {
        chrome.storage.local.get(request.keys, (result) => {
            sendResponse(result);
        });
        return true; // 비동기 응답을 위해 true 반환
    }
});