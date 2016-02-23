# -*- coding: utf-8 -*-

from pysimplesoap.client import SoapClient

class SoapReceiver:
    def __init__(self):
        self.client = SoapClient(
            location="http://search.nalog.ru/WebServices/Public/DownloadService.asmx",
            action='http://search.nalog.ru/WebServices/Public/DownloadService.asmx/',
            namespace="http://search.nalog.ru/WebServices/Public/DownloadService.asmx",
            soap_ns='soap', trace=False, ns=False)

    # return (intver, strver, url)
    def get_update_list(self):
        response = self.client.GetAllDownloadFileInfo()

        assert response, "Response is null"

        for DownloadFileInfo in response.GetAllDownloadFileInfoResponse.GetAllDownloadFileInfoResult.DownloadFileInfo:
            yield dict(intver=int(DownloadFileInfo.VersionId), strver=str(DownloadFileInfo.TextVersion),
                       delta_url=str(DownloadFileInfo.FiasDeltaXmlUrl),
                       complete_url=str(DownloadFileInfo.FiasCompleteXmlUrl))
