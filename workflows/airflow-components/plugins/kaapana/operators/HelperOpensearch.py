from opensearchpy import OpenSearch


class HelperOpensearch():
    study_uid_tag = "0020000D StudyInstanceUID_keyword"
    series_uid_tag = "0020000E SeriesInstanceUID_keyword"
    SOPInstanceUID_tag = "00080018 SOPInstanceUID_keyword"
    modality_tag = "00080060 Modality_keyword"

    host = "opensearch-service.meta.svc"
    port = "9200"
    index = "meta-index"
    auth = None
    # auth = ('admin', 'admin') # For testing only. Don't store credentials in code.

    os_client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        timeout=2,
        # ca_certs = ca_certs_path
    )

    @staticmethod
    def get_query_cohort(query, index=None):
        index = index if index is not None else HelperOpensearch.index
        print("Getting cohort for query: {}".format(query))
        print("index: {}".format(index))

        queryDict = {}
        queryDict["query"] = query
        queryDict["_source"] = {"includes": [HelperOpensearch.study_uid_tag, HelperOpensearch.series_uid_tag,
                                             HelperOpensearch.SOPInstanceUID_tag, HelperOpensearch.modality_tag]}

        try:
            res = HelperOpensearch.os_client.search(index=[index], body=queryDict, size=10000, from_=0)
        except Exception as e:
            print("ERROR in search!")
            print(e)
            return None

        hits = res['hits']['hits']

        return hits

    @staticmethod
    def get_series_metadata(series_uid, index=None):
        index = index if index is not None else HelperOpensearch.index
        queryDict = {}
        queryDict["query"] = {'bool': {
            'must':
            [
                {'match_all': {}},
                {'match_phrase': {
                    '0020000E SeriesInstanceUID_keyword.keyword': {'query': series_uid}}},
            ], 'filter': [], 'should': [], 'must_not': []}}

        queryDict["_source"] = {}

        try:
            res = HelperOpensearch.os_client.search(index=[index], body=queryDict, size=10000, from_=0)
        except Exception as e:
            print("ERROR in search!")
            print(e)
            return None

        hits = res['hits']['hits']

        if len(hits) != 1:
            print("Opensearch got multiple results for series_uid: {}".format(series_uid))
            print("This is unexpected and treated as error -> abort!")
            return None

        hit = hits[0]["_source"]
        return hit

    @staticmethod
    def delete_by_query(query, index=None):
        index = index if index is not None else HelperOpensearch.index
        try:
            res = HelperOpensearch.os_client.delete_by_query(index=index, body=query)
            print(res)
        except Exception as e:
            print(f"# ERROR deleting from Opensearch: {str(e)}")
            print(f"# query: {query}")
            exit(1)
