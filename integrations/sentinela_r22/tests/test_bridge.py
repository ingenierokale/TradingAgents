import unittest

from integrations.sentinela_r22.bridge import summarize_sentinela_report


def sample():
    return {
        "name": "SENTINELA_MULTIAGENTE_MCP_LAB",
        "offline_only": True,
        "generated_utc": "2026-10-22T00:00:00Z",
        "roles": {
            "ANALISTA_PATRON": {"read_evaluations": 15},
            "ANALISTA_LATENCIA": {"late_decisions": 2,
                                 "provider_tick_timestamp_verified": False},
            "ANALISTA_ADN": {"context_hypothesis_counts": {"filter_A": 7}},
            "AUDITOR_RESULTADOS": {"authority": "SOLO_LECTURA",
                                  "verified_trades": 3,
                                  "verified_outcomes": {"WIN": 2, "LOSS": 1}},
            "DIRECTOR_MCP": {"authority": "NINGUNA_COMPRA", "alerts": []},
        },
    }


class BridgeTests(unittest.TestCase):
    def test_verified_and_readonly(self):
        result = summarize_sentinela_report(sample())
        self.assertFalse(result["execution_authority"])
        self.assertEqual(result["verified"]["total"], 3)
        self.assertEqual(result["verified"]["winrate_excluding_draw_pct"], 66.67)

    def test_unverified_result_not_invented(self):
        data = sample()
        data["roles"]["AUDITOR_RESULTADOS"]["verified_trades"] = 0
        data["roles"]["AUDITOR_RESULTADOS"]["verified_outcomes"] = {}
        result = summarize_sentinela_report(data)
        self.assertIsNone(result["verified"]["winrate_excluding_draw_pct"])

    def test_inconsistent_count_rejected(self):
        data = sample()
        data["roles"]["AUDITOR_RESULTADOS"]["verified_trades"] = 4
        with self.assertRaises(ValueError):
            summarize_sentinela_report(data)

    def test_cannot_authorize_orders(self):
        data = sample()
        data["roles"]["DIRECTOR_MCP"]["authority"] = "BUY"
        with self.assertRaises(ValueError):
            summarize_sentinela_report(data)


if __name__ == "__main__":
    unittest.main()
