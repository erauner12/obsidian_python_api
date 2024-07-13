#!/usr/bin/env python

# Doc: https://coddingtonbear.github.io/obsidian-local-rest-api/#/
import logging
import os
from datetime import datetime
from typing import Any, Dict, List
from requests import Request, Session
from requests.exceptions import RequestException
import json

logger = logging.getLogger(__name__)

class ObsidianFiles:
    def __init__(
        self,
        api_url: str,
        token: str,
        public_cert: str or None = None,
        public_key: str or None = None,
    ):
        self.api_url = api_url
        self.token = token
        self.headers = {
            "accept": "text/markdown",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "text/markdown",
        }
        self.cert = (public_cert, public_key) if public_cert and public_key else None

    def _send_request(self, method: str, cmd: str, data: str or None = None) -> Any:
        try:
            s = Session()
            _request = Request(
                method,
                f"{self.api_url}{cmd}",
                headers=self.headers,
                data=data,
            )
            prepped = s.prepare_request(_request)
            resp = s.send(prepped, cert=self.cert, verify=False)
            resp.raise_for_status()
            return resp
        except RequestException as e:
            logger.error(f"Request failed: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def _get_active_file_content(self) -> str or None:
        try:
            resp = self._send_request("GET", cmd="/active/")
            if resp and resp.status_code == 200:
                logger.info("Successfully retrieved active file content!")
                return resp.text
            else:
                logger.error(f"Failed to get active file content. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in get_active_file_content: {e}")
            return None

    def _append_content_to_active_file(self, content: str) -> bool:
        self.headers["accept"] = "*/*"
        try:
            resp = self._send_request("POST", cmd="/active/", data=content)
            if resp and resp.status_code == 200:
                logger.info("Added content successfully!")
                return True
            else:
                logger.error(f"Failed to append content. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in append_content_to_active_file: {e}")
            return False

    def _update_content_of_active_file(self, content: str) -> bool:
        try:
            resp = self._send_request("POST", cmd="/active/", data=content)
            if resp and resp.status_code == 200:
                logger.info("Updated content successfully!")
                return True
            else:
                logger.error(f"Failed to update content. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in update_content_of_active_file: {e}")
            return False

    def _delete_active_file(self) -> bool:
        try:
            resp = self._send_request("DELETE", cmd="/active/")
            if resp and resp.status_code == 204:
                logger.info("Deleted the currently active file in Obsidian.")
                return True
            else:
                logger.error(f"Failed to delete active file. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in delete_active_file: {e}")
            return False

    def _insert_content_of_active_file(
        self,
        content: str,
        heading: str,
        insert_position: str,
        heading_boundary: str = "",
    ) -> bool:
        self.headers["accept"] = "*/*"
        self.headers["Heading"] = heading
        self.headers["Content-Insertion-Position"] = insert_position
        self.headers["Content-Type"] = "text/markdown"
        if heading_boundary:
            self.headers["Heading-Boundary"] = heading_boundary

        try:
            resp = self._send_request("PATCH", cmd="/active/", data=content)
            if resp and resp.status_code == 200:
                logger.info("Inserted the content successfully!")
                return True
            else:
                logger.error(f"Failed to insert content. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in insert_content_of_active_file: {e}")
            return False

    def _get_target_file_content(self, target_filename: str, return_format: str = "text/markdown") -> str or Dict[str, Any] or None:
        if return_format == "json":
            self.headers["accept"] = "application/vnd.olrapi.note+json"
        else:
            self.headers["accept"] = "text/markdown"

        try:
            resp = self._send_request("GET", cmd=f"/vault/{target_filename}")
            if resp and resp.status_code == 200:
                logger.info(f"Got the content of {target_filename} successfully!")
                if return_format == "json":
                    return resp.json()
                else:
                    content = resp.json().get("data", [])
                    return bytes(content).decode('utf-8') if content else ""
            else:
                logger.error(f"Failed to get content of {target_filename}. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in get_target_file_content: {e}")
            return None

    def _create_or_update_file(self, target_filename: str, content: str) -> bool:
        self.headers["accept"] = "*/*"
        try:
            resp = self._send_request("PUT", cmd=f"/vault/{target_filename}", data=content)
            if resp and resp.status_code in [200, 204]:
                logger.info(f"Created/Updated {target_filename} successfully!")
                return True
            else:
                logger.error(f"Failed to create/update {target_filename}. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in create_or_update_file: {e}")
            return False

    def _delete_target_file(self, target_filename: str) -> bool:
        try:
            resp = self._send_request("DELETE", cmd=f"/vault/{target_filename}")
            if resp and resp.status_code in [200, 204]:
                logger.info(f"Deleted {target_filename} successfully!")
                return True
            else:
                logger.error(f"Failed to delete {target_filename}. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in delete_target_file: {e}")
            return False

    def _append_content_to_target_file(self, target_filename: str, content: str) -> bool:
        self.headers["accept"] = "*/*"
        try:
            resp = self._send_request("PUT", cmd=f"/vault/{target_filename}", data=content)
            if resp and resp.status_code == 200:
                logger.info(f"Appended content to {target_filename} successfully!")
                return True
            else:
                logger.error(f"Failed to append content to {target_filename}. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in append_content_to_target_file: {e}")
            return False

    def _insert_content_of_target_file(
        self,
        target_filename: str,
        content: str,
        heading: str,
        insert_position: str,
        heading_boundary: str = "",
    ) -> bool:
        self.headers["accept"] = "*/*"
        self.headers["Heading"] = heading
        self.headers["Content-Insertion-Position"] = insert_position
        self.headers["Content-Type"] = "text/markdown"
        if heading_boundary:
            self.headers["Heading-Boundary"] = heading_boundary

        try:
            resp = self._send_request("PATCH", cmd=f"/vault/{target_filename}", data=content)
            if resp and resp.status_code == 200:
                logger.info(f"Inserted content to {target_filename} successfully!")
                return True
            else:
                logger.error(f"Failed to insert content to {target_filename}. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in insert_content_of_target_file: {e}")
            return False

    def _list_files_in_vault(self, target_dir: str) -> Dict[str, any] or None:
        try:
            self.headers["accept"] = "application/json"
            resp = self._send_request("GET", cmd=f"/vault/{target_dir}")
            if resp and resp.status_code == 200:
                logger.info(f"Got the list of files in {target_dir} successfully!")
                return resp.json()
            else:
                logger.error(f"Failed to list files in {target_dir}. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in list_files_in_vault: {e}")
            return None

    def _list_commands(self) -> List[Dict[str, any]] or None:
        try:
            self.headers["accept"] = "application/json"
            resp = self._send_request("GET", cmd="/commands/")
            if resp and resp.status_code == 200:
                logger.info("Fetched all the commands successfully!")
                return resp.json()
            else:
                logger.error(f"Failed to fetch commands. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in list_commands: {e}")
            return None

    def _run_command(self, command_id: str) -> bool:
        try:
            self.headers["accept"] = "*/*"
            resp = self._send_request("POST", cmd=f"/commands/{command_id}")
            if resp and resp.status_code == 200:
                logger.info("The command is executed successfully!")
                return True
            else:
                logger.error(f"Failed to execute command. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in run_command: {e}")
            return False

    def _search_with_query(self, request_body: str or dict) -> List[dict[str, any]] or None:
        try:
            self.headers["accept"] = "application/json"
            self.headers["Content-Type"] = (
                "application/vnd.olrapi.dataview.dql+txt"
                if isinstance(request_body, str)
                else "application/vnd.olrapi.jsonlogic+json"
            )

            req_body = request_body if isinstance(request_body, str) else json.dumps(request_body)

            resp = self._send_request("POST", cmd="/search/", data=req_body)
            if resp and resp.status_code == 200:
                logger.info("Got the search results!")
                return resp.json()
            else:
                logger.error(f"Failed to perform search. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in search_with_query: {e}")
            return None

    def _search_with_simple_query(self, query: str, content_length: int = 100) -> List[dict[str, any]] or None:
        try:
            self.headers["accept"] = "application/json"
            resp = self._send_request("POST", cmd=f"/search/{query}&contextLength={content_length}")
            if resp and resp.status_code == 200:
                logger.info("Got the search results!")
                return resp.json()
            else:
                logger.error(f"Failed to perform simple search. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in search_with_simple_query: {e}")
            return None

    def _search_with_gui(self, query: str, content_length: int = 100) -> List[dict[str, any]] or None:
        try:
            self.headers["accept"] = "application/json"
            resp = self._send_request("POST", cmd=f"/search/gui/?{query}&contextLength={content_length}")
            if resp and resp.status_code == 200:
                logger.info("Got the GUI search results!")
                return resp.json()
            else:
                logger.error(f"Failed to perform GUI search. Status code: {resp.status_code if resp else 'Unknown'}")
                return None
        except Exception as e:
            logger.error(f"Error in search_with_gui: {e}")
            return None

    def _open_file(self, target_filename: str, new_leaf: bool = False) -> bool:
        try:
            self.headers["accept"] = "application/json"
            resp = self._send_request("POST", cmd=f"/open/{target_filename}?newLeaf={new_leaf}")
            if resp and resp.status_code == 200:
                logger.info(f"Opened {target_filename} in Obsidian.")
                return True
            else:
                logger.error(f"Failed to open {target_filename}. Status code: {resp.status_code if resp else 'Unknown'}")
                return False
        except Exception as e:
            logger.error(f"Error in open_file: {e}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("ObsidianFiles class is ready to use.")
