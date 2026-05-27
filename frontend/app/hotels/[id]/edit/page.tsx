import { getHotel } from "@/lib/api";
import { HotelForm } from "@/components/hotels/HotelForm";

export default async function EditHotelPage({ params }: { params: { id: string } }) {
  const hotel = await getHotel(params.id);
  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Editar hotel</h1>
      <p className="text-sm text-gray-500 mb-6">{hotel.name}</p>
      <HotelForm hotel={hotel} />
    </div>
  );
}
