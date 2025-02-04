#define CINTERFACE
#define COBJMACROS

#include <ExDisp.h>
#include <ShObjIdl.h>
#include <ShlObj.h>
#include <objbase.h>

HRESULT FindDesktopFolderView(REFIID riid, void** ppv) {
    if (!ppv)
        return E_POINTER;
    *ppv = NULL;

    IShellWindows* pShellWindows = NULL;
    HRESULT hr = CoCreateInstance(&CLSID_ShellWindows, NULL, CLSCTX_ALL,
        &IID_IShellWindows, &pShellWindows);

    IDispatch* pDispatch = NULL;
    if (SUCCEEDED(hr)) {
        VARIANT vtLoc = { .vt = VT_I4, .lVal = CSIDL_DESKTOP };
        VARIANT vtEmpty = { .vt = VT_EMPTY };
        long lhwnd = 0;
        hr = IShellWindows_FindWindowSW(pShellWindows, &vtLoc, &vtEmpty, SWC_DESKTOP,
            &lhwnd, SWFO_NEEDDISPATCH, &pDispatch);
    }

    IServiceProvider* pServiceProvider = NULL;
    if (SUCCEEDED(hr)) {
        hr = IDispatch_QueryInterface(pDispatch, &IID_IServiceProvider,
            &pServiceProvider);
    }

    IShellBrowser* pBrowser = NULL;
    if (SUCCEEDED(hr)) {
        hr = IServiceProvider_QueryService(pServiceProvider, &SID_STopLevelBrowser,
            &IID_IShellBrowser, &pBrowser);
    }

    IShellView* pShellView = NULL;
    if (SUCCEEDED(hr)) {
        hr = IShellBrowser_QueryActiveShellView(pBrowser, &pShellView);
    }

    if (SUCCEEDED(hr)) {
        hr = IShellView_QueryInterface(pShellView, riid, ppv);
    }

    if (pShellView)
        IShellView_Release(pShellView);
    if (pBrowser)
        IShellBrowser_Release(pBrowser);
    if (pServiceProvider)
        IServiceProvider_Release(pServiceProvider);
    if (pDispatch)
        IDispatch_Release(pDispatch);
    if (pShellWindows)
        IShellWindows_Release(pShellWindows);

    return hr;
}

HRESULT RepositionItemByIndex(int index, POINT pos) {
    HRESULT hr = S_OK;

    if (index < 0)
        hr = DISP_E_BADINDEX;

    IFolderView* pView = NULL;
    if (SUCCEEDED(hr)) {
        hr = FindDesktopFolderView(&IID_IFolderView, &pView);
    }

    int count = 0;
    if (SUCCEEDED(hr)) {
        hr = IFolderView_ItemCount(pView, SVGIO_ALLVIEW, &count);
        if (SUCCEEDED(hr) && (index >= count))
            hr = DISP_E_BADINDEX;
    }

    IEnumIDList* pIDList = NULL;
    if (SUCCEEDED(hr)) {
        hr = IFolderView_Items(pView, SVGIO_ALLVIEW | SVGIO_FLAG_VIEWORDER,
            &IID_IEnumIDList, &pIDList);
    }

    ITEMIDLIST* pIDL = NULL;
    int current_idx = -1;
    while (SUCCEEDED(hr) && current_idx < index) {
        CoTaskMemFree(pIDL);
        pIDL = NULL;

        hr = IEnumIDList_Next(pIDList, 1, &pIDL, NULL);
        if (hr != S_OK)
            break;

        ++current_idx;
    }

    if (SUCCEEDED(hr) && (index == current_idx)) {
        PCITEMID_CHILD apidl[1] = { pIDL };
        hr = IFolderView_SelectAndPositionItems(pView, 1, apidl, &pos,
            SVSI_POSITIONITEM);
    }

    CoTaskMemFree(pIDL);
    if (pIDList)
        IEnumIDList_Release(pIDList);
    if (pView)
        IFolderView_Release(pView);

    return hr;
}

__declspec(dllexport) HRESULT RepositionItem(int index, int x, int y) {
    HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) return hr;

    POINT pos = { .x = x, .y = y };
    hr = RepositionItemByIndex(index, pos);

    CoUninitialize();
    return hr;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
    return TRUE;
}