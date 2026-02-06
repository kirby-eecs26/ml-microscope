import unittest
from unittest.mock import patch
from io import StringIO
import json
import backend.error
from backend.server import * #(apiHealth, checkCords, moveButton, captureImg, listCaptures, mjpeg_stream_url,
                            #captureVideo)


class TestServer(unittest.TestCase):

    def __innit__(self):
        self.good_payload = {
            "filename": "test",
            "temporary": False,
            "use_video_port": False,
            "bayer": True,
            "annotations": {
                "Notes": "test1"
            },
            "tags": []
        }

        self.bad_payload = {}


    # def test_apiHealth_has_connection(self):
    #     assert apiHealth() == 200
    #
    #
    # def test_apiHealth_no_microscope(self):
    #     assert apiHealth() == False


    def test_checkCords_xyz_in_of_bounds(self):
        assert checkCords(4, 4, 4) == True
        assert checkCords(4, -4, -4) == True
        assert checkCords(-4, 4, -4) == True
        assert checkCords(-4, -4, 4) == True
        assert checkCords(4, 4, -4) == True
        assert checkCords(4, -4, 4) == True
        assert checkCords(-4, 4, 4) == True


    def test_checkCords_xyz_out_of_bounds(self):
        assert checkCords(-85001, -85001, -85001) == False
        assert checkCords(85001, 85001, 85001) == False
        assert checkCords(-85001, 85001, 85001) == False
        assert checkCords(85001, -85001, 85001) == False
        assert checkCords(85001, 85001, -85001) == False
        assert checkCords(-85001, -85001, 85001) == False
        assert checkCords(-85001, 85001, -85001) == False
        assert checkCords(85001, -85001, -85001) == False


    def test_moveButton_correct_bounds(self):
        return_avl = moveButton(4, 4, 4)

        assert return_avl != Exception
        assert type(return_avl) is list or dict


    def test_moveButton_incorrect_bounds(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            moveButton(-85001, -85001, -85001)
            self.assertEqual(mock_stdout.getvalue(), "moveButton\ncheckCords\nMicroscope couldn't move, out of bounds or motor error\n")


    def test_captureImg_good_return(self):
        good_payload = {
            "filename": "test",
            "temporary": False,
            "use_video_port": False,
            "bayer": True,
            "annotations": {
                "Notes": "test1"
            },
            "tags": []
        }

        return_val = captureImg(good_payload)
        assert type(return_val) is dict


    def test_captureImg_bad_return(self):
        good_payload = {
            "filename": "test",
            "temporary": False,
            "use_video_port": False,
            "bayer": True,
            "annotations": {
                "Notes": "test1"
            },
            "tags": []
        }

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            captureImg(good_payload)
            self.assertEqual(mock_stdout.getvalue(), "captureImg\nCamera error: could not take img\n")


    def test_listCaptures_good_return(self):
        return_val = listCaptures()
        assert return_val != Exception
        assert type(return_val) is list


    def test_listCaptures_exception(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            listCaptures()
            self.assertEqual(mock_stdout.getvalue(), "listCaptures\nCamera error: could not list captures\n")


    def test_captureVideo(self):
        good_payload = {
            "filename": "test",
            "temporary": False,
            "use_video_port": False,
            "bayer": True,
            "annotations": {
                "Notes": "test1"
            },
            "tags": []
        }

        video1 = captureVideo(30, good_payload)
        assert type(video1) is list
        # print(video1)
        # print(len(video1))
        assert len(video1) == 8

        video2 = captureVideo(60, good_payload)
        # print(video2)
        # print(len(video2))
        assert len(video2) == 15

        video3 = captureVideo(30, good_payload, 5)
        # print(video3)
        # print(len(video3))
        assert len(video3) == 3

        video4 = captureVideo(60, good_payload, 5)
        # print(video4)
        # print(len(video4))
        assert len(video4) == 5