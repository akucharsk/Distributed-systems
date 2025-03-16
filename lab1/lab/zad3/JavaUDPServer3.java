package zad3;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

public class JavaUDPServer3 {
    public static void main(String[] args) {
        DatagramSocket socket = null;
        final int portNumber = args.length > 0 ? Integer.parseInt(args[0]) : 8008;
        final String host = args.length > 1 ? args[1] : "localhost";

        try {
            socket = new DatagramSocket(portNumber, InetAddress.getByName(host));
            byte[] buffer = new byte[1024];

            while (true) {
                Arrays.fill(buffer, (byte) 0);
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);

                int clientMsg = ByteBuffer.wrap(buffer).order(ByteOrder.LITTLE_ENDIAN).getInt();
                System.out.println("Received number from client: ");
                System.out.println(clientMsg);
                System.out.println();

                byte[] response = ByteBuffer.allocate(4).putInt(clientMsg + 1).array();
                DatagramPacket responsePacket = new DatagramPacket(response, response.length, packet.getAddress(), packet.getPort());
                socket.send(responsePacket);
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