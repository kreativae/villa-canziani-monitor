-- ============================================================
-- Villa Canziani & Donato — Hotel Price Monitor
-- Initial schema
-- ============================================================

create extension if not exists "uuid-ossp";

-- Hotels registry
create table hotels (
  id          uuid primary key default uuid_generate_v4(),
  name        text not null,
  official_url text,
  booking_url text,
  booking_id  text,            -- booking.com property ID if known
  category    text,            -- boutique, pousada, resort, etc.
  region      text default 'Praia do Patacho',
  notes       text,
  engine      text,            -- omnibees | simplotel | cloudbeds | fastbooking | custom
  active      boolean not null default true,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- Room types per hotel
create table room_types (
  id          uuid primary key default uuid_generate_v4(),
  hotel_id    uuid not null references hotels(id) on delete cascade,
  name        text not null,
  max_guests  integer,
  description text,
  created_at  timestamptz not null default now()
);

-- Price snapshots — one row per scrape result
create table price_snapshots (
  id                  uuid primary key default uuid_generate_v4(),
  hotel_id            uuid not null references hotels(id) on delete cascade,
  room_type_id        uuid references room_types(id) on delete set null,
  source              text not null check (source in ('official','booking')),
  price               numeric(10,2),
  currency            char(3) not null default 'BRL',
  check_in            date,
  check_out           date,
  guests              integer default 2,
  breakfast_included  boolean,
  cancellation_policy text,
  availability        boolean,
  raw_data            jsonb,
  scraped_at          timestamptz not null default now()
);

-- Scrape job log
create table scrape_jobs (
  id          uuid primary key default uuid_generate_v4(),
  hotel_id    uuid references hotels(id) on delete cascade,  -- null = all hotels
  triggered_by text default 'manual',                        -- manual | scheduler
  status      text not null default 'pending'
              check (status in ('pending','running','completed','failed')),
  hotels_total integer,
  hotels_done  integer default 0,
  hotels_failed integer default 0,
  error_log   jsonb,
  started_at  timestamptz,
  completed_at timestamptz,
  created_at  timestamptz not null default now()
);

-- Indexes for common queries
create index on price_snapshots(hotel_id, scraped_at desc);
create index on price_snapshots(hotel_id, source, check_in);
create index on scrape_jobs(status, created_at desc);

-- Auto-update updated_at on hotels
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger hotels_updated_at
  before update on hotels
  for each row execute function set_updated_at();

-- ============================================================
-- Seed: initial hotels list
-- ============================================================
insert into hotels (name, official_url, booking_url, category, engine, notes) values
-- ── URLs confirmados via pesquisa ──────────────────────────────────────────
('Origem Patacho | Hotel Design',
  'https://origempatacho.com.br',
  'https://www.booking.com/hotel/br/origem-patacho-design.pt-br.html',
  'hotel', null, null),

('Hotel Zai Patacho',
  'https://zaipatacho.com.br',
  'https://www.booking.com/hotel/br/zai-patacho.html',
  'hotel', null, null),

('Pedras do Patacho • Hotel Boutique Experience',
  'https://pedrasdopatacho.com.br',
  'https://www.booking.com/hotel/br/pousada-pedras-do-patacho.html',
  'boutique', null, null),

('Casa Brasileira Hotel Galeria',
  'https://casabrasileirahotel.com.br',
  'https://www.booking.com/hotel/br/casa-brasileira-galeria.html',
  'hotel', 'omnibees', 'Motor Omnibees confirmado'),

('Pousada Praia do Patacho',
  null,
  'https://www.booking.com/hotel/br/pousada-praia-do-patacho.html',
  'pousada', null, null),

('Pousada Reserva do Patacho',
  'https://www.pousadareservadopatacho.com.br',
  'https://www.booking.com/hotel/br/pousada-reserva-do-patacho.html',
  'pousada', null, null),

('Pousada Samba Pa Ti',
  'https://www.pousadasambapati.com.br',
  'https://www.booking.com/hotel/br/pousada-samba-pa-ti.html',
  'pousada', null, null),

('Pousada Quinta do Patacho',
  null,
  'https://www.booking.com/hotel/br/pousada-quinta-do-patacho.html',
  'pousada', null, null),

('Pousada Iandê Patacho',
  'https://pousadaiandepatacho.com.br',
  'https://www.booking.com/hotel/br/pousada-iande-patacho.html',
  'pousada', null, null),

('Carrapicho Patacho',
  null,
  'https://www.booking.com/hotel/br/carrapicho-patacho-porto-de-pedras-al.html',
  'pousada', null, null),

('Pousada Xuê',
  'https://www.pousadaxue.com.br',
  'https://www.booking.com/hotel/br/pousada-xue.html',
  'pousada', null, null),

('Aldeia Beijupirá Pousada',
  'https://www.aldeiabeijupira.com.br',
  'https://www.booking.com/hotel/br/pousada-aldeia-beijupira-porto-de-pedras.html',
  'pousada', null, null),

('Vila do Patacho',
  'http://viladopatacho.com.br',
  'https://www.booking.com/hotel/br/pousada-vila-do-patacho.html',
  'pousada', null, null),

('Patacho Eco Residence',
  null, null,
  'hotel', null, 'Possível loteamento/condomínio — verificar se tem hospedagem ativa'),

('Villa Pantai Milagres Exclusive Hotel',
  'https://www.villapantai.com.br',
  'https://www.booking.com/hotel/br/pousada-villa-pantai.html',
  'hotel', null, null),

('Pousada Rangai',
  'https://pousadarangai.com',
  'https://www.booking.com/hotel/br/pousada-rangai.html',
  'pousada', null, 'Localizada em Maragogi / Praia de Antunes'),

('Pousada Tutaméia',
  null, null,
  'pousada', null, 'URL não encontrada — verificar nome correto'),

('Villa Tatuamunha',
  'https://pousadavillatatuamunha.com',
  'https://www.booking.com/hotel/br/pousada-villa-tatuamunha.html',
  'hotel', null, null),

('Paru Boutique Hotel',
  'https://paruhotel.com.br',
  'https://www.booking.com/hotel/br/villas-do-paru-praia-de-marceneiro.html',
  'boutique', null, null),

('Pousada Casotas',
  'https://www.casotas.com.br',
  'https://www.booking.com/hotel/br/casotas-da-laje.html',
  'pousada', null, null),

('Pousada Peixe do Mato',
  'https://www.peixedomato.com.br',
  'https://www.booking.com/hotel/br/sitio-peixe-do-mato-sao-miguel-dos-milagres.html',
  'pousada', null, null),

('Naim Hotel',
  'https://naimmilagres.com.br',
  'https://www.booking.com/hotel/br/naim-studios-milagres.html',
  'hotel', null, null),

('Kaçuá Milagres',
  'https://kacuamilagres.com.br',
  'https://www.booking.com/hotel/br/kacua-milagres.html',
  'pousada', null, null),

('Angá Beach Hotel',
  'https://www.angahotel.com.br',
  'https://www.booking.com/hotel/br/anga.html',
  'hotel', null, null),

('Côté Sud Patacho',
  'https://www.villacotesud.com.br',
  'https://www.booking.com/hotel/br/pousada-ca-ta-c-sud.html',
  'boutique', null, null),

('Morada do Toque',
  null,
  'https://www.booking.com/hotel/br/morada-do-toque-sao-miguel-dos-milagres.html',
  'pousada', null, null),

('Vila Naiá',
  null, null,
  'pousada', null, 'URL não confirmada na região — verificar nome'),

('Pousada Marceneiro',
  'https://www.pousadamarceneiro.com.br',
  'https://www.booking.com/hotel/br/pousada-marceneiro.html',
  'pousada', null, null),

('Casa Acayu',
  'https://casaacayu.com.br',
  'https://www.booking.com/hotel/br/casa-acayu.html',
  'pousada', null, null),

('Pousada Rota Ecológica',
  'https://pousadarotaecologica.com.br',
  'https://www.booking.com/hotel/br/casa-rota-ecologica.html',
  'pousada', null, null),

('Toca do Caranguejo',
  'https://tocadocaranguejo.com.br',
  'https://www.booking.com/hotel/br/toca-do-caranguejo.html',
  'pousada', null, null),

('Pousada Santo Milagre',
  null, null,
  'pousada', null, 'URL não encontrada — verificar nome correto'),

('Villa Kamby Milagres',
  null,
  'https://www.booking.com/hotel/br/villa-kamby-sao-miguel-dos-milagres.html',
  'hotel', null, null),

('Porto Kahuna Beach Hotel',
  null, null,
  'hotel', null, 'URL não encontrada — verificar nome correto'),

-- #35 Pousada Villa Pantai é o mesmo empreendimento que #15 Villa Pantai (nome alternativo)
('Pousada Villa Pantai',
  'https://www.villapantai.com.br',
  'https://www.booking.com/hotel/br/pousada-villa-pantai.html',
  'pousada', null, 'Mesmo empreendimento que "Villa Pantai Milagres Exclusive Hotel" — verificar duplicidade'),

('Milagres do Toque Beach Club',
  null, null,
  'hotel', null, 'Beach club/restaurante — verificar se tem hospedagem'),

('Odoiá Maragogi Restaurante & Estalagem',
  'https://odoiamaragogi.com.br',
  'https://www.booking.com/hotel/br/odoia-maragogi-restaurante-e-estalagem.html',
  'pousada', null, null),

('Pousada Jangadas da Caponga',
  null, null,
  'pousada', null, 'URL não confirmada em Alagoas — verificar nome correto'),

('Villa Mango Beach Bungalows',
  null, null,
  'hotel', null, 'URL não confirmada em Alagoas — verificar nome correto'),

('Pousada Ricoco',
  'https://pousadaricoco.com.br',
  'https://www.booking.com/hotel/br/pousada-ricoco.html',
  'pousada', null, null);
