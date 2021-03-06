Feature: Client Config

    Scenario: Read client config
        When we get "client_config"
        Then we get existing resource
        """
        {
            "config": {
                "xmpp_auth": false,
                "attachments_max_files": 10,
                "attachments_max_size": 8388608
            }
        }
        """
