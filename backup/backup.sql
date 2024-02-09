PGDMP  %            	        |            RezeptDB    16.1 (Debian 16.1-1.pgdg120+1)    16.1 (Debian 16.1-1.pgdg120+1) 9    Z           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            [           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            \           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            ]           1262    16384    RezeptDB    DATABASE     u   CREATE DATABASE "RezeptDB" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';
    DROP DATABASE "RezeptDB";
             
   jessonardo    false            �            1259    17077 	   bewertung    TABLE     �   CREATE TABLE public.bewertung (
    id integer NOT NULL,
    rezept_id integer,
    sterne integer,
    kommentar character varying
);
    DROP TABLE public.bewertung;
       public         heap 
   jessonardo    false            �            1259    17076    bewertung_id_seq    SEQUENCE     �   CREATE SEQUENCE public.bewertung_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.bewertung_id_seq;
       public       
   jessonardo    false    222            ^           0    0    bewertung_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.bewertung_id_seq OWNED BY public.bewertung.id;
          public       
   jessonardo    false    221            �            1259    17091    bild    TABLE     i   CREATE TABLE public.bild (
    id integer NOT NULL,
    rezept_id integer,
    path character varying
);
    DROP TABLE public.bild;
       public         heap 
   jessonardo    false            �            1259    17090    bild_id_seq    SEQUENCE     �   CREATE SEQUENCE public.bild_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.bild_id_seq;
       public       
   jessonardo    false    224            _           0    0    bild_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public.bild_id_seq OWNED BY public.bild.id;
          public       
   jessonardo    false    223            �            1259    17040    rezept    TABLE     �   CREATE TABLE public.rezept (
    id integer NOT NULL,
    titel character varying,
    anweisung character varying,
    hauptrezept_id integer
);
    DROP TABLE public.rezept;
       public         heap 
   jessonardo    false            �            1259    17039    rezept_id_seq    SEQUENCE     �   CREATE SEQUENCE public.rezept_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.rezept_id_seq;
       public       
   jessonardo    false    216            `           0    0    rezept_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.rezept_id_seq OWNED BY public.rezept.id;
          public       
   jessonardo    false    215            �            1259    17104 
   rezept_tag    TABLE     `   CREATE TABLE public.rezept_tag (
    rezept_id integer NOT NULL,
    tag_id integer NOT NULL
);
    DROP TABLE public.rezept_tag;
       public         heap 
   jessonardo    false            �            1259    17063    schritt    TABLE     �   CREATE TABLE public.schritt (
    id integer NOT NULL,
    rezept_id integer,
    schritt_nummer integer,
    anweisung character varying
);
    DROP TABLE public.schritt;
       public         heap 
   jessonardo    false            �            1259    17062    schritt_id_seq    SEQUENCE     �   CREATE SEQUENCE public.schritt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.schritt_id_seq;
       public       
   jessonardo    false    220            a           0    0    schritt_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.schritt_id_seq OWNED BY public.schritt.id;
          public       
   jessonardo    false    219            �            1259    17054    tag    TABLE     X   CREATE TABLE public.tag (
    id integer NOT NULL,
    bezeichnung character varying
);
    DROP TABLE public.tag;
       public         heap 
   jessonardo    false            �            1259    17053 
   tag_id_seq    SEQUENCE     �   CREATE SEQUENCE public.tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 !   DROP SEQUENCE public.tag_id_seq;
       public       
   jessonardo    false    218            b           0    0 
   tag_id_seq    SEQUENCE OWNED BY     9   ALTER SEQUENCE public.tag_id_seq OWNED BY public.tag.id;
          public       
   jessonardo    false    217            �            1259    17120    zutat    TABLE     �   CREATE TABLE public.zutat (
    id integer NOT NULL,
    rezept_id integer NOT NULL,
    schritt_id integer NOT NULL,
    menge character varying,
    einheit character varying,
    bezeichnung character varying
);
    DROP TABLE public.zutat;
       public         heap 
   jessonardo    false            �            1259    17119    zutat_id_seq    SEQUENCE     �   CREATE SEQUENCE public.zutat_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.zutat_id_seq;
       public       
   jessonardo    false    227            c           0    0    zutat_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.zutat_id_seq OWNED BY public.zutat.id;
          public       
   jessonardo    false    226            �           2604    17080    bewertung id    DEFAULT     l   ALTER TABLE ONLY public.bewertung ALTER COLUMN id SET DEFAULT nextval('public.bewertung_id_seq'::regclass);
 ;   ALTER TABLE public.bewertung ALTER COLUMN id DROP DEFAULT;
       public       
   jessonardo    false    221    222    222            �           2604    17094    bild id    DEFAULT     b   ALTER TABLE ONLY public.bild ALTER COLUMN id SET DEFAULT nextval('public.bild_id_seq'::regclass);
 6   ALTER TABLE public.bild ALTER COLUMN id DROP DEFAULT;
       public       
   jessonardo    false    223    224    224            �           2604    17043 	   rezept id    DEFAULT     f   ALTER TABLE ONLY public.rezept ALTER COLUMN id SET DEFAULT nextval('public.rezept_id_seq'::regclass);
 8   ALTER TABLE public.rezept ALTER COLUMN id DROP DEFAULT;
       public       
   jessonardo    false    215    216    216            �           2604    17066 
   schritt id    DEFAULT     h   ALTER TABLE ONLY public.schritt ALTER COLUMN id SET DEFAULT nextval('public.schritt_id_seq'::regclass);
 9   ALTER TABLE public.schritt ALTER COLUMN id DROP DEFAULT;
       public       
   jessonardo    false    220    219    220            �           2604    17057    tag id    DEFAULT     `   ALTER TABLE ONLY public.tag ALTER COLUMN id SET DEFAULT nextval('public.tag_id_seq'::regclass);
 5   ALTER TABLE public.tag ALTER COLUMN id DROP DEFAULT;
       public       
   jessonardo    false    217    218    218            �           2604    17123    zutat id    DEFAULT     d   ALTER TABLE ONLY public.zutat ALTER COLUMN id SET DEFAULT nextval('public.zutat_id_seq'::regclass);
 7   ALTER TABLE public.zutat ALTER COLUMN id DROP DEFAULT;
       public       
   jessonardo    false    226    227    227            R          0    17077 	   bewertung 
   TABLE DATA           E   COPY public.bewertung (id, rezept_id, sterne, kommentar) FROM stdin;
    public       
   jessonardo    false    222   �=       T          0    17091    bild 
   TABLE DATA           3   COPY public.bild (id, rezept_id, path) FROM stdin;
    public       
   jessonardo    false    224   >       L          0    17040    rezept 
   TABLE DATA           F   COPY public.rezept (id, titel, anweisung, hauptrezept_id) FROM stdin;
    public       
   jessonardo    false    216   *>       U          0    17104 
   rezept_tag 
   TABLE DATA           7   COPY public.rezept_tag (rezept_id, tag_id) FROM stdin;
    public       
   jessonardo    false    225   G>       P          0    17063    schritt 
   TABLE DATA           K   COPY public.schritt (id, rezept_id, schritt_nummer, anweisung) FROM stdin;
    public       
   jessonardo    false    220   d>       N          0    17054    tag 
   TABLE DATA           .   COPY public.tag (id, bezeichnung) FROM stdin;
    public       
   jessonardo    false    218   �>       W          0    17120    zutat 
   TABLE DATA           W   COPY public.zutat (id, rezept_id, schritt_id, menge, einheit, bezeichnung) FROM stdin;
    public       
   jessonardo    false    227   �>       d           0    0    bewertung_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.bewertung_id_seq', 1, false);
          public       
   jessonardo    false    221            e           0    0    bild_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.bild_id_seq', 1, false);
          public       
   jessonardo    false    223            f           0    0    rezept_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.rezept_id_seq', 1, false);
          public       
   jessonardo    false    215            g           0    0    schritt_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.schritt_id_seq', 1, false);
          public       
   jessonardo    false    219            h           0    0 
   tag_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('public.tag_id_seq', 1, false);
          public       
   jessonardo    false    217            i           0    0    zutat_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.zutat_id_seq', 1, false);
          public       
   jessonardo    false    226            �           2606    17084    bewertung bewertung_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.bewertung
    ADD CONSTRAINT bewertung_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.bewertung DROP CONSTRAINT bewertung_pkey;
       public         
   jessonardo    false    222            �           2606    17098    bild bild_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.bild
    ADD CONSTRAINT bild_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.bild DROP CONSTRAINT bild_pkey;
       public         
   jessonardo    false    224            �           2606    17047    rezept rezept_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.rezept
    ADD CONSTRAINT rezept_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.rezept DROP CONSTRAINT rezept_pkey;
       public         
   jessonardo    false    216            �           2606    17108    rezept_tag rezept_tag_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY public.rezept_tag
    ADD CONSTRAINT rezept_tag_pkey PRIMARY KEY (rezept_id, tag_id);
 D   ALTER TABLE ONLY public.rezept_tag DROP CONSTRAINT rezept_tag_pkey;
       public         
   jessonardo    false    225    225            �           2606    17070    schritt schritt_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.schritt
    ADD CONSTRAINT schritt_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.schritt DROP CONSTRAINT schritt_pkey;
       public         
   jessonardo    false    220            �           2606    17061    tag tag_pkey 
   CONSTRAINT     J   ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);
 6   ALTER TABLE ONLY public.tag DROP CONSTRAINT tag_pkey;
       public         
   jessonardo    false    218            �           2606    17127    zutat zutat_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.zutat
    ADD CONSTRAINT zutat_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.zutat DROP CONSTRAINT zutat_pkey;
       public         
   jessonardo    false    227            �           2606    17085 "   bewertung bewertung_rezept_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.bewertung
    ADD CONSTRAINT bewertung_rezept_id_fkey FOREIGN KEY (rezept_id) REFERENCES public.rezept(id);
 L   ALTER TABLE ONLY public.bewertung DROP CONSTRAINT bewertung_rezept_id_fkey;
       public       
   jessonardo    false    3239    216    222            �           2606    17099    bild bild_rezept_id_fkey    FK CONSTRAINT     z   ALTER TABLE ONLY public.bild
    ADD CONSTRAINT bild_rezept_id_fkey FOREIGN KEY (rezept_id) REFERENCES public.rezept(id);
 B   ALTER TABLE ONLY public.bild DROP CONSTRAINT bild_rezept_id_fkey;
       public       
   jessonardo    false    224    216    3239            �           2606    17048 !   rezept rezept_hauptrezept_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.rezept
    ADD CONSTRAINT rezept_hauptrezept_id_fkey FOREIGN KEY (hauptrezept_id) REFERENCES public.rezept(id);
 K   ALTER TABLE ONLY public.rezept DROP CONSTRAINT rezept_hauptrezept_id_fkey;
       public       
   jessonardo    false    216    3239    216            �           2606    17109 $   rezept_tag rezept_tag_rezept_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.rezept_tag
    ADD CONSTRAINT rezept_tag_rezept_id_fkey FOREIGN KEY (rezept_id) REFERENCES public.rezept(id);
 N   ALTER TABLE ONLY public.rezept_tag DROP CONSTRAINT rezept_tag_rezept_id_fkey;
       public       
   jessonardo    false    225    3239    216            �           2606    17114 !   rezept_tag rezept_tag_tag_id_fkey    FK CONSTRAINT     }   ALTER TABLE ONLY public.rezept_tag
    ADD CONSTRAINT rezept_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);
 K   ALTER TABLE ONLY public.rezept_tag DROP CONSTRAINT rezept_tag_tag_id_fkey;
       public       
   jessonardo    false    3241    225    218            �           2606    17071    schritt schritt_rezept_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.schritt
    ADD CONSTRAINT schritt_rezept_id_fkey FOREIGN KEY (rezept_id) REFERENCES public.rezept(id);
 H   ALTER TABLE ONLY public.schritt DROP CONSTRAINT schritt_rezept_id_fkey;
       public       
   jessonardo    false    220    3239    216            �           2606    17128    zutat zutat_rezept_id_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.zutat
    ADD CONSTRAINT zutat_rezept_id_fkey FOREIGN KEY (rezept_id) REFERENCES public.rezept(id);
 D   ALTER TABLE ONLY public.zutat DROP CONSTRAINT zutat_rezept_id_fkey;
       public       
   jessonardo    false    216    3239    227            �           2606    17133    zutat zutat_schritt_id_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.zutat
    ADD CONSTRAINT zutat_schritt_id_fkey FOREIGN KEY (schritt_id) REFERENCES public.schritt(id);
 E   ALTER TABLE ONLY public.zutat DROP CONSTRAINT zutat_schritt_id_fkey;
       public       
   jessonardo    false    227    3243    220            R      x������ � �      T      x������ � �      L      x������ � �      U      x������ � �      P      x������ � �      N      x������ � �      W      x������ � �     