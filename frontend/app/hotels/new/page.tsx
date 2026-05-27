import { HotelForm } from "@/components/hotels/HotelForm";

export default function NewHotelPage() {
  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Cadastrar novo hotel</h1>
      <p className="text-sm text-gray-500 mb-6">
        Preencha os dados e URLs para iniciar o monitoramento.
      </p>
      <HotelForm />
    </div>
  );
}
