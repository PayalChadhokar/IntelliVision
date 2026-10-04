import unittest
from unittest.mock import patch

from services.fir_service import create_fir_draft


class TestFIRService(unittest.TestCase):

    @patch(
        "services.fir_service.get_db_connection",
        return_value=None
    )
    def test_database_connection_failure(
        self,
        mock_connection
    ):

        with self.assertRaises(
            RuntimeError
        ):

            create_fir_draft(
                complaint_id=1,
                fir_data={}
            )


if __name__ == "__main__":
    unittest.main()