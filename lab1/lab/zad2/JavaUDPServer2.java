package zad2;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public class JavaUDPServer2 {
    public static void main(String[] args) {
        DatagramSocket socket = null;
        final int portNumber = args.length > 0 ? Integer.parseInt(args[0]) : 8008;
        final String host = args.length > 1 ? args[1] : "localhost";

        try {
            socket = new DatagramSocket(portNumber, InetAddress.getByName(host));

            final int bufferSize = 1024;
            byte[] buffer = new byte[bufferSize];

            while (true) {
                Arrays.fill(buffer, (byte) 0);
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);
                if (new String(packet.getData()).startsWith("kill")) {
                    System.out.println("Client killed me");
                    break;
                }
                String message = new StringBuilder("Received from Python client ")
                        .append(packet.getAddress().toString())
                        .append(':')
                        .append(packet.getPort())
                        .append("\n  ")
                        .append(new String(packet.getData(), StandardCharsets.UTF_8))
                        .append("\n\n")
                        .toString();

                System.out.println(message);
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
