from __future__ import annotations

import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tumor_tree_pipeline.contracts import SMCConfig
from tumor_tree_pipeline.cpp_backend import _terminate_process_group, run_smc_cpp


class CppBackendLifecycleTests(unittest.TestCase):
    def test_process_group_already_gone_is_still_waited(self) -> None:
        process = mock.Mock(pid=321)
        with mock.patch(
            "tumor_tree_pipeline.cpp_backend.os.killpg",
            side_effect=ProcessLookupError,
        ):
            _terminate_process_group(process)
        process.wait.assert_called_once_with(timeout=10)

    def test_process_group_timeout_escalates_to_sigkill(self) -> None:
        process = mock.Mock(pid=321)
        process.wait.side_effect = [subprocess.TimeoutExpired("cmd", 10), None]
        with mock.patch("tumor_tree_pipeline.cpp_backend.os.killpg") as killpg:
            _terminate_process_group(process)
        self.assertEqual(
            killpg.call_args_list,
            [mock.call(321, signal.SIGTERM), mock.call(321, signal.SIGKILL)],
        )
        self.assertEqual(
            process.wait.call_args_list,
            [mock.call(timeout=10), mock.call()],
        )

    def test_interrupt_terminates_and_waits_for_cpp_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_path = root / "model_input.tsv"
            input_path.write_text("mutation_id\nsite-1\n", encoding="utf-8")
            output_path = root / "repeat"
            process = mock.Mock(pid=321, returncode=130)
            process.communicate.side_effect = KeyboardInterrupt()
            process.wait.return_value = 0

            with (
                mock.patch("tumor_tree_pipeline.cpp_backend.find_inference_binary", return_value=Path("/bin/true")),
                mock.patch("tumor_tree_pipeline.cpp_backend.subprocess.Popen", return_value=process) as popen,
                mock.patch("tumor_tree_pipeline.cpp_backend.os.killpg") as killpg,
            ):
                with self.assertRaises(KeyboardInterrupt):
                    run_smc_cpp(
                        integrated_input=input_path,
                        outdir=output_path,
                        config=SMCConfig(seed=1, num_nodes=2, particles=2, max_annealing_stages=1),
                    )

            popen.assert_called_once()
            self.assertTrue(popen.call_args.kwargs["start_new_session"])
            killpg.assert_called_once_with(321, signal.SIGTERM)
            process.wait.assert_called_once_with(timeout=10)


if __name__ == "__main__":
    unittest.main()
