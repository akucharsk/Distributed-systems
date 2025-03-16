package zad1;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;
import java.util.Scanner;

public class JavaUDPClient1 {
    public static void main(String[] args) {
        DatagramSocket socket = null;
        final String host = "127.0.0.1";
        final int bufferSize = 1024;
        try {
            int port = Integer.parseInt(args[0]);
            int serverPort = args.length > 1 ? Integer.parseInt(args[1]) : 8008;
            socket = new DatagramSocket(port);
            InetAddress address = InetAddress.getByName(host);
            byte[] buffer = new byte[bufferSize];
            BufferedReader in = new BufferedReader(new InputStreamReader(System.in), 1024);

            while (true) {
                Arrays.fill(buffer, (byte) 0);
                String message = in.readLine();
                if (message.equals("exit")) {
                    System.out.println("Exiting");
                    break;
                }
                DatagramPacket packet = new DatagramPacket(message.getBytes(), message.getBytes().length, address, serverPort);
                System.out.printf("Sending message:\n %s\n", message);
                socket.send(packet);
                if (message.equals("kill")) {
                    System.out.println("Killing server");
                    break;
                }
                System.out.println("---Message sent---");
                DatagramPacket recvPacket = new DatagramPacket(buffer, buffer.length);
                socket.receive(recvPacket);
                System.out.printf("Received message from server:\n %s\n\n", new String(recvPacket.getData()));
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (socket != null) {
                socket.close();
            }
        }
    }
}
